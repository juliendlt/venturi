from __future__ import annotations

from typing import TYPE_CHECKING

from pyspark.sql import functions as F

from ...core.commons.reader import read_table
from ...core.commons.writer import write_table
from ...core.context import Context
from ...utils.lambert93 import lambert93_to_latitude, lambert93_to_longitude
from ..base import Pipeline

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def transform(turbine: DataFrame, farm: DataFrame) -> DataFrame:
    """Dimension aérogénérateur : une ligne par aérogénérateur, prête pour l'analyse.

    Chaque aérogénérateur reçoit sa position en longitude / latitude (WGS84),
    calculée à partir des coordonnées Lambert-93 du silver, et les attributs de son
    parc (nom, état, statut), pour être lu sans jointure.

    La jointure est à gauche : un aérogénérateur dont le parc est absent du registre
    des parcs est conservé, avec les attributs du parc à null.
    """
    t = turbine.alias("t")
    f = farm.alias("f")

    return t.join(f, F.col("t.farm_id") == F.col("f.farm_id"), "left").select(
        F.col("t.turbine_id").alias("turbine_id"),
        F.col("t.turbine_name").alias("turbine_name"),
        F.col("t.farm_id").alias("farm_id"),
        F.col("f.farm_name").alias("farm_name"),
        F.col("f.operating_state").alias("farm_operating_state"),
        F.col("f.permit_status").alias("farm_permit_status"),
        F.col("f.commissioning_date").alias("farm_commissioning_date"),
        F.col("t.insee_code").alias("insee_code"),
        F.col("t.commune_name").alias("commune_name"),
        F.col("t.department_code").alias("department_code"),
        F.col("t.region_code").alias("region_code"),
        F.col("t.capacity_mw").alias("capacity_mw"),
        F.col("t.tip_height_m").alias("tip_height_m"),
        F.col("t.hub_height_m").alias("hub_height_m"),
        F.col("t.rotor_diameter_m").alias("rotor_diameter_m"),
        F.col("t.elevation_m").alias("elevation_m"),
        F.col("t.manufacturer").alias("manufacturer"),
        F.col("t.model").alias("model"),
        lambert93_to_longitude(F.col("t.x_lambert93"), F.col("t.y_lambert93")).alias("longitude"),
        lambert93_to_latitude(F.col("t.x_lambert93"), F.col("t.y_lambert93")).alias("latitude"),
        F.col("t.updated_at").alias("updated_at"),
    )


class GoldWindTurbine(Pipeline):
    name = "gold.wind_turbine"
    description = "Dimension aérogénérateur : position WGS84 et attributs du parc"

    table_key = "wind_turbine"
    farm_key = "wind_farm"

    def run(self, context: Context) -> None:
        turbine_source = context.tables.silver[self.table_key]
        farm_source = context.tables.silver[self.farm_key]
        table = context.tables.gold[self.table_key]

        context.logger.info("Lecture de %s", turbine_source.full_table_name)
        turbine = read_table(context.spark, turbine_source)

        context.logger.info("Lecture de %s", farm_source.full_table_name)
        farm = read_table(context.spark, farm_source)

        context.logger.info("Écriture de %s", table.full_table_name)
        write_table(transform(turbine, farm), table, mode="overwrite")
