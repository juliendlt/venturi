from __future__ import annotations

from typing import TYPE_CHECKING

from pyspark.sql import functions as F

from ...core.commons.reader import read_table
from ...core.commons.writer import write_table
from ...core.context import Context
from ..base import Pipeline

if TYPE_CHECKING:
    from pyspark.sql import DataFrame

def transform(bronze: DataFrame) -> DataFrame:
    """Parcs éoliens typés, renommés en anglais, une ligne par parc.

    Seules les colonnes utiles à l'analyse sont gardées. Le bronze a une ligne par parc et par commune d'implantation. Les colonnes de
    commune (`code_insee`, `nom_commune`, `code_dept`, `code_reg`) sont les seules à
    varier pour un même parc : elles sont retirées, puis les lignes dédoublonnées.
    La commune reste disponible par aérogénérateur dans `silver.wind_turbine`.

    Les conversions sont strictes (`cast` en mode ANSI) : une valeur qui ne se
    convertit pas fait échouer le pipeline au lieu de devenir null.
    """
    return bronze.select(
        F.col("id_parc").alias("farm_id"),
        F.trim(F.col("nom_usuel")).alias("farm_name"),
        F.col("puissance_parc_mw").cast("double").alias("capacity_mw"),
        F.col("nombre_aerogenerateur").cast("int").alias("turbine_count"),
        F.col("nombre_poste_livraison").cast("int").alias("substation_count"),
        F.col("date_depot_demande_autorisation").cast("date").alias("permit_request_date"),
        F.col("date_mise_en_service").cast("date").alias("commissioning_date"),
        F.col("date_debut_demantelement").cast("date").alias("decommissioning_date"),
        F.col("etat_parc").alias("operating_state"),
        F.col("statut_admin").alias("permit_type"),
        F.col("statut_parc").alias("permit_status"),
        # x_parc / y_parc sont déjà en WGS84 : geom_wgs84_point (EWKB) est redondant.
        F.col("x_parc").cast("double").alias("longitude"),
        F.col("y_parc").cast("double").alias("latitude"),
        F.col("date_maj").cast("timestamp").alias("updated_at"),
    ).distinct()


class SilverWindFarm(Pipeline):
    name = "silver.wind_farm"
    description = "Parcs éoliens : typage, renommage, une ligne par parc"

    table_key = "wind_farm"

    def run(self, context: Context) -> None:
        source = context.tables.bronze[self.table_key]
        table = context.tables.silver[self.table_key]

        context.logger.info("Lecture de %s", source.full_table_name)
        df = transform(read_table(context.spark, source))

        context.logger.info("Écriture de %s", table.full_table_name)
        write_table(df, table, mode="overwrite")
