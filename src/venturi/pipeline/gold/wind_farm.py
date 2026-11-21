from __future__ import annotations

from typing import TYPE_CHECKING

from pyspark.sql import functions as F

from ...core.commons.reader import read_table
from ...core.commons.writer import write_table
from ...core.context import Context
from ..base import Pipeline

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def summarize_turbines(turbine: DataFrame) -> DataFrame:
    """Résumé des aérogénérateurs recensés, une ligne par parc."""
    return turbine.groupBy("farm_id").agg(
        F.count("*").cast("int").alias("located_turbine_count"),
        F.round(F.sum("capacity_mw"), 2).alias("located_capacity_mw"),
        F.max("tip_height_m").alias("max_tip_height_m"),
        # Un parc peut s'étendre sur plusieurs départements : on garde le plus
        # représenté parmi ses aérogénérateurs.
        F.mode("department_code").alias("department_code"),
        F.mode("region_code").alias("region_code"),
        F.mode("manufacturer").alias("main_manufacturer"),
    )


def transform(farm: DataFrame, turbine: DataFrame) -> DataFrame:
    """Dimension parc : une ligne par parc, enrichie du résumé de ses aérogénérateurs.

    `turbine_count` et `capacity_mw` sont les valeurs déclarées dans le registre des
    parcs ; `located_turbine_count` et `located_capacity_mw` sont recalculées à
    partir des aérogénérateurs recensés. Les deux peuvent différer.

    La jointure est à gauche : un parc sans aérogénérateur recensé est conservé,
    avec `located_turbine_count` à 0.
    """
    f = farm.alias("f")
    s = summarize_turbines(turbine).alias("s")

    return f.join(s, F.col("f.farm_id") == F.col("s.farm_id"), "left").select(
        F.col("f.farm_id").alias("farm_id"),
        F.col("f.farm_name").alias("farm_name"),
        F.col("s.department_code").alias("department_code"),
        F.col("s.region_code").alias("region_code"),
        F.col("f.capacity_mw").alias("capacity_mw"),
        F.col("f.turbine_count").alias("turbine_count"),
        F.coalesce(F.col("s.located_turbine_count"), F.lit(0)).alias("located_turbine_count"),
        F.col("s.located_capacity_mw").alias("located_capacity_mw"),
        F.col("s.max_tip_height_m").alias("max_tip_height_m"),
        F.col("s.main_manufacturer").alias("main_manufacturer"),
        F.col("f.substation_count").alias("substation_count"),
        F.col("f.permit_request_date").alias("permit_request_date"),
        F.col("f.commissioning_date").alias("commissioning_date"),
        F.col("f.decommissioning_date").alias("decommissioning_date"),
        F.col("f.operating_state").alias("operating_state"),
        F.col("f.permit_type").alias("permit_type"),
        F.col("f.permit_status").alias("permit_status"),
        F.col("f.longitude").alias("longitude"),
        F.col("f.latitude").alias("latitude"),
        F.col("f.updated_at").alias("updated_at"),
    )


class GoldWindFarm(Pipeline):
    name = "gold.wind_farm"
    description = "Dimension parc : attributs du parc et résumé de ses aérogénérateurs"

    table_key = "wind_farm"
    turbine_key = "wind_turbine"

    def run(self, context: Context) -> None:
        farm_source = context.tables.silver[self.table_key]
        turbine_source = context.tables.silver[self.turbine_key]
        table = context.tables.gold[self.table_key]

        context.logger.info("Lecture de %s", farm_source.full_table_name)
        farm = read_table(context.spark, farm_source)

        context.logger.info("Lecture de %s", turbine_source.full_table_name)
        turbine = read_table(context.spark, turbine_source)

        context.logger.info("Écriture de %s", table.full_table_name)
        write_table(transform(farm, turbine), table, mode="overwrite")
