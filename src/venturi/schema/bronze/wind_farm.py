"""Schéma bronze du registre OREOL des parcs éoliens (`parc.csv`).

En bronze, toutes les colonnes sont lues en chaîne : le typage se fait en silver.
"""

from pyspark.sql.types import StringType, StructField, StructType

wind_farm_schema = StructType(
    [
        StructField("id_parc", StringType(), True),
        StructField("nom_usuel", StringType(), True),
        StructField("raison_sociale", StringType(), True),
        StructField("siret", StringType(), True),
        StructField("puissance_parc_mw", StringType(), True),
        StructField("nombre_aerogenerateur", StringType(), True),
        StructField("nombre_poste_livraison", StringType(), True),
        StructField("code_insee", StringType(), True),
        StructField("nom_commune", StringType(), True),
        StructField("code_dept", StringType(), True),
        StructField("code_reg", StringType(), True),
        StructField("date_depot_demande_autorisation", StringType(), True),
        StructField("date_delivrance_avis_autorite_environnementale", StringType(), True),
        StructField("date_delivrance_autorisation", StringType(), True),
        StructField("date_debut_construction", StringType(), True),
        StructField("date_mise_en_service", StringType(), True),
        StructField("date_debut_demantelement", StringType(), True),
        StructField("etat_parc", StringType(), True),
        StructField("statut_admin", StringType(), True),
        StructField("statut_parc", StringType(), True),
        StructField("date_arrete_prefectoral_complementaire_renouvellement", StringType(), True),
        StructField("renouvellement", StringType(), True),
        StructField("geom_wgs84_point", StringType(), True),
        StructField("x_parc", StringType(), True),
        StructField("y_parc", StringType(), True),
        StructField("date_maj", StringType(), True),
    ]
)
