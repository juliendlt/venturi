# 0007 – Schémas bronze déclarés en Python, toutes colonnes en chaîne

- **Statut** : Acceptée
- **Date** : 2026-11-16

## Contexte

Les pipelines bronze lisaient les CSV OREOL sans schéma : Spark prenait toutes les
colonnes en chaîne, sans contrôle sur les noms ni sur le nombre de colonnes. Activer
l'inférence de types aurait abîmé certaines valeurs : les identifiants
`id_parc = 0000000034` ou les codes INSEE perdraient leurs zéros de tête, et le
type d'une colonne pourrait changer d'un fichier à l'autre.

## Décision

- Chaque table bronze a un schéma `StructType` déclaré dans
  `src/venturi/schema/bronze/<clé>.py`, sous la même clé que `config/tables.yaml`
  (`wind_farm_schema`, `wind_turbine_schema`).
- En bronze, toutes les colonnes sont en `StringType` : la donnée est conservée
  telle que la source la livre, et le typage se fait en silver.
- Chaque colonne est écrite explicitement, avec un `StructField` par ligne, même si
  c'est répétitif : le schéma doit pouvoir être modifié à la main, colonne par
  colonne, par exemple pour changer un type. Il n'est jamais généré par une boucle.
- Le schéma est passé au `CsvReader` ; la lecture reste en `FAILFAST`, donc une
  ligne malformée fait échouer le pipeline.

## Conséquences

- Les noms et l'ordre des colonnes de la table bronze sont fixés par le code, et non
  plus par l'en-tête du fichier.
- Une colonne ajoutée ou retirée dans la source impose de modifier le schéma.
- Les conversions (nombres, dates, géométrie) et leurs règles de rejet sont
  centralisées en silver.
- Une table bronze déjà écrite avec un autre schéma doit être supprimée, ou réécrite
  avec `overwrite_schema`, avant de pouvoir l'écraser.

## Alternatives écartées

- **Inférence de types (`inferSchema`)** : instable d'un fichier à l'autre et
  destructrice pour les codes et identifiants.
- **Typage dès le bronze** : mêle ingestion et règles métier, et fait échouer
  l'ingestion pour une valeur mal formée.
- **Schéma déclaré en YAML** : redondant avec les types Spark, et sans l'aide de
  l'éditeur.
- **Schéma généré à partir d'une liste de colonnes** : plus court, mais un type ne
  peut plus être changé pour une seule colonne.
