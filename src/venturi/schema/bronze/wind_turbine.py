"""Schéma bronze du registre OREOL des aérogénérateurs (`aerogenerator.csv`).

En bronze, toutes les colonnes sont lues en chaîne : le typage se fait en silver.
"""

from pyspark.sql.types import StringType, StructField, StructType

wind_turbine_schema = StructType(
    [
        StructField("id_aerogenerateur", StringType(), True),
        StructField("nom_eolienne", StringType(), True),
        StructField("id_parc", StringType(), True),
        StructField("nom_usuel", StringType(), True),
        StructField("code_insee", StringType(), True),
        StructField("nom_commune", StringType(), True),
        StructField("code_dept", StringType(), True),
        StructField("code_reg", StringType(), True),
        StructField("puissance_mw", StringType(), True),
        StructField("hauteur_totale", StringType(), True),
        StructField("hauteur_mat_nacelle", StringType(), True),
        StructField("diametre_rotor", StringType(), True),
        StructField("cote_ngf", StringType(), True),
        StructField("periode_allumage", StringType(), True),
        StructField("type_feu", StringType(), True),
        StructField("constructeur", StringType(), True),
        StructField("reference_modele", StringType(), True),
        StructField("x_aerogenerateur", StringType(), True),
        StructField("y_aerogenerateur", StringType(), True),
        StructField("epsg", StringType(), True),
        StructField("etat_parc", StringType(), True),
        StructField("statut_parc", StringType(), True),
        StructField("date_maj", StringType(), True),
    ]
)
