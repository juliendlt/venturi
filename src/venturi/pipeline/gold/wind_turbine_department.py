from __future__ import annotations

from typing import TYPE_CHECKING

from pyspark.sql import functions as F

from ...core.commons.reader import read_table
from ...core.commons.writer import write_table
from ...core.context import Context
from ..base import Pipeline

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

# Valeur de `farm_operating_state` (reprise telle quelle de la source) qui désigne
# un parc en service.
OPERATING_STATE = "En exploitation"


def transform(turbine: DataFrame) -> DataFrame:
    """Indicateurs des aérogénérateurs par département, une ligne par département.

    Le département est celui de la commune d'implantation de chaque aérogénérateur.
    Un parc à cheval sur deux départements est compté dans `farm_count` de chacun.

    `longitude` / `latitude` sont le centre des aérogénérateurs du département ;
    les colonnes `min_` / `max_` donnent leur emprise.
    """
    is_operating = F.col("farm_operating_state") == F.lit(OPERATING_STATE)

    return turbine.groupBy("region_code", "department_code").agg(
        F.count_distinct("farm_id").cast("int").alias("farm_count"),
        F.count("*").cast("int").alias("turbine_count"),
        F.round(F.sum("capacity_mw"), 2).alias("capacity_mw"),
        F.count_if(is_operating).cast("int").alias("operating_turbine_count"),
        F.round(F.coalesce(F.sum(F.when(is_operating, F.col("capacity_mw"))), F.lit(0.0)), 2).alias("operating_capacity_mw"),
        F.round(F.avg("capacity_mw"), 2).alias("avg_turbine_capacity_mw"),
        F.max("tip_height_m").alias("max_tip_height_m"),
        F.mode("manufacturer").alias("main_manufacturer"),
        F.avg("longitude").alias("longitude"),
        F.avg("latitude").alias("latitude"),
        F.min("longitude").alias("min_longitude"),
        F.max("longitude").alias("max_longitude"),
        F.min("latitude").alias("min_latitude"),
        F.max("latitude").alias("max_latitude"),
    )


class GoldWindTurbineDepartment(Pipeline):
    name = "gold.wind_turbine_department"
    description = "Agrégat des aérogénérateurs par département"

    source_key = "wind_turbine"
    table_key = "wind_turbine_department"

    def run(self, context: Context) -> None:
        source = context.tables.gold[self.source_key]
        table = context.tables.gold[self.table_key]

        context.logger.info("Lecture de %s", source.full_table_name)
        df = transform(read_table(context.spark, source))

        context.logger.info("Écriture de %s", table.full_table_name)
        write_table(df, table, mode="overwrite")
