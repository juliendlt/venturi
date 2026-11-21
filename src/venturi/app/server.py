"""Carte interactive des parcs éoliens : `venturi-map`.

Au démarrage, les tables gold (dimensions et agrégats) sont lues une fois avec Spark et gardées en
mémoire (quelques milliers de lignes), puis Spark est arrêté. Un petit serveur HTTP
de la bibliothèque standard sert ensuite la page et les jeux de données.
"""

from __future__ import annotations

import argparse
import gzip
import json
import logging
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pyspark.sql import functions as F

from ..config import load_tables
from ..core.commons.reader import read_table
from ..core.spark import build_spark

STATIC_DIR = Path(__file__).parent / "static"

logger = logging.getLogger("venturi.app")


def load_data() -> dict[str, bytes]:
    """Lit les tables gold et retourne, par route, le JSON compressé à servir."""
    tables = load_tables()
    spark = build_spark("venturi-map")
    try:
        regions = (
            read_table(spark, tables.gold["wind_turbine_region"])
            .select(
                F.col("region_code").alias("code"),
                F.col("department_count").alias("department_count"),
                F.col("farm_count").alias("farm_count"),
                F.col("turbine_count").alias("turbine_count"),
                F.col("capacity_mw").alias("capacity_mw"),
                F.col("operating_turbine_count").alias("operating_turbine_count"),
                F.col("operating_capacity_mw").alias("operating_capacity_mw"),
                F.col("avg_turbine_capacity_mw").alias("avg_turbine_capacity_mw"),
                F.col("max_tip_height_m").alias("max_tip_height_m"),
                F.col("main_manufacturer").alias("manufacturer"),
                F.round(F.col("longitude"), 5).alias("lon"),
                F.round(F.col("latitude"), 5).alias("lat"),
                F.round(F.col("min_longitude"), 5).alias("west"),
                F.round(F.col("max_longitude"), 5).alias("east"),
                F.round(F.col("min_latitude"), 5).alias("south"),
                F.round(F.col("max_latitude"), 5).alias("north"),
            )
            .collect()
        )
        departments = (
            read_table(spark, tables.gold["wind_turbine_department"])
            .select(
                F.col("department_code").alias("code"),
                F.col("region_code").alias("region"),
                F.col("farm_count").alias("farm_count"),
                F.col("turbine_count").alias("turbine_count"),
                F.col("capacity_mw").alias("capacity_mw"),
                F.col("operating_turbine_count").alias("operating_turbine_count"),
                F.col("operating_capacity_mw").alias("operating_capacity_mw"),
                F.col("avg_turbine_capacity_mw").alias("avg_turbine_capacity_mw"),
                F.col("max_tip_height_m").alias("max_tip_height_m"),
                F.col("main_manufacturer").alias("manufacturer"),
                F.round(F.col("longitude"), 5).alias("lon"),
                F.round(F.col("latitude"), 5).alias("lat"),
                F.round(F.col("min_longitude"), 5).alias("west"),
                F.round(F.col("max_longitude"), 5).alias("east"),
                F.round(F.col("min_latitude"), 5).alias("south"),
                F.round(F.col("max_latitude"), 5).alias("north"),
            )
            .collect()
        )
        farms = (
            read_table(spark, tables.gold["wind_farm"])
            .select(
                F.col("farm_id").alias("id"),
                F.col("farm_name").alias("name"),
                F.col("department_code").alias("department"),
                F.col("capacity_mw").alias("capacity_mw"),
                F.col("turbine_count").alias("turbine_count"),
                F.col("located_turbine_count").alias("located_turbine_count"),
                F.col("main_manufacturer").alias("manufacturer"),
                F.col("commissioning_date").cast("string").alias("commissioning_date"),
                F.col("operating_state").alias("state"),
                F.col("permit_status").alias("permit_status"),
                F.round(F.col("longitude"), 5).alias("lon"),
                F.round(F.col("latitude"), 5).alias("lat"),
            )
            .collect()
        )
        turbines = (
            read_table(spark, tables.gold["wind_turbine"])
            .select(
                F.col("turbine_id").alias("id"),
                F.col("turbine_name").alias("name"),
                F.col("farm_id").alias("farm_id"),
                F.col("commune_name").alias("commune"),
                F.col("capacity_mw").alias("capacity_mw"),
                F.col("tip_height_m").alias("tip_height_m"),
                F.col("hub_height_m").alias("hub_height_m"),
                F.col("rotor_diameter_m").alias("rotor_diameter_m"),
                F.col("manufacturer").alias("manufacturer"),
                F.col("model").alias("model"),
                F.round(F.col("longitude"), 5).alias("lon"),
                F.round(F.col("latitude"), 5).alias("lat"),
            )
            .collect()
        )
    finally:
        spark.stop()

    logger.info(
        "%d régions, %d départements, %d parcs et %d aérogénérateurs chargés",
        len(regions), len(departments), len(farms), len(turbines),
    )
    return {
        "/api/regions": _to_gzipped_json([row.asDict() for row in regions]),
        "/api/departments": _to_gzipped_json([row.asDict() for row in departments]),
        "/api/farms": _to_gzipped_json([row.asDict() for row in farms]),
        "/api/turbines": _to_gzipped_json([row.asDict() for row in turbines]),
    }


def _to_gzipped_json(rows: list[dict]) -> bytes:
    return gzip.compress(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def build_handler(data: dict[str, bytes]) -> type[BaseHTTPRequestHandler]:
    index = gzip.compress((STATIC_DIR / "index.html").read_bytes())

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            path = self.path.split("?", 1)[0]
            if path == "/":
                self._send(index, "text/html; charset=utf-8")
            elif path in data:
                self._send(data[path], "application/json; charset=utf-8")
            else:
                self.send_error(HTTPStatus.NOT_FOUND)

        def _send(self, body: bytes, content_type: str) -> None:
            # Tous les navigateurs acceptent gzip : le contenu est servi compressé.
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            logger.debug(format, *args)

    return Handler


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="venturi-map", description="Carte interactive des parcs éoliens.")
    parser.add_argument("--port", type=int, default=8050)
    parser.add_argument("--no-browser", action="store_true", help="n'ouvre pas le navigateur")
    args = parser.parse_args(argv)

    logging.basicConfig(level="INFO", format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    logger.info("Lecture des tables gold (démarrage de Spark)…")
    data = load_data()

    # Écoute sur la boucle locale uniquement : l'app n'est pas exposée sur le réseau.
    server = ThreadingHTTPServer(("127.0.0.1", args.port), build_handler(data))
    url = f"http://127.0.0.1:{args.port}/"
    logger.info("Carte disponible sur %s (Ctrl+C pour arrêter)", url)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Arrêt")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
