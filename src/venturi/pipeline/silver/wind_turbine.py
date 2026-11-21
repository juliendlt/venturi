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
    """Aérogénérateurs typés et renommés en anglais, une ligne par aérogénérateur.

    Le grain du bronze est conservé (`id_aerogenerateur` est unique). Seules les
    colonnes utiles à l'analyse sont gardées : les attributs du parc recopiés par la
    source (nom, état, statut) se lisent dans `silver.wind_farm` par `farm_id`, et
    le balisage lumineux est écarté.

    Les conversions sont strictes (`cast` en mode ANSI) : une valeur qui ne se
    convertit pas fait échouer le pipeline au lieu de devenir null.
    """
    return bronze.select(
        F.col("id_aerogenerateur").alias("turbine_id"),
        F.trim(F.col("nom_eolienne")).alias("turbine_name"),
        F.col("id_parc").alias("farm_id"),
        F.col("code_insee").alias("insee_code"),
        F.col("nom_commune").alias("commune_name"),
        F.col("code_dept").alias("department_code"),
        F.col("code_reg").alias("region_code"),
        F.col("puissance_mw").cast("double").alias("capacity_mw"),
        F.col("hauteur_totale").cast("double").alias("tip_height_m"),
        F.col("hauteur_mat_nacelle").cast("double").alias("hub_height_m"),
        F.col("diametre_rotor").cast("double").alias("rotor_diameter_m"),
        F.col("cote_ngf").cast("double").alias("elevation_m"),
        # La source mélange les casses : SENVION / Senvion, GAMESA / Gamesa.
        F.upper(F.trim(F.col("constructeur"))).alias("manufacturer"),
        F.trim(F.col("reference_modele")).alias("model"),
        # Coordonnées projetées en Lambert-93 : la colonne epsg vaut toujours 2154.
        F.col("x_aerogenerateur").cast("double").alias("x_lambert93"),
        F.col("y_aerogenerateur").cast("double").alias("y_lambert93"),
        F.col("date_maj").cast("timestamp").alias("updated_at"),
    )


class SilverWindTurbine(Pipeline):
    name = "silver.wind_turbine"
    description = "Aérogénérateurs : typage, renommage, colonnes utiles"

    table_key = "wind_turbine"

    def run(self, context: Context) -> None:
        source = context.tables.bronze[self.table_key]
        table = context.tables.silver[self.table_key]

        context.logger.info("Lecture de %s", source.full_table_name)
        df = transform(read_table(context.spark, source))

        context.logger.info("Écriture de %s", table.full_table_name)
        write_table(df, table, mode="overwrite")
