# 0010 – Dimensions gold des parcs et des aérogénérateurs

- **Statut** : Proposée
- **Date** : 2026-11-21

## Contexte

Le silver livre deux tables typées, `wind_farm` et `wind_turbine`
([0009](0009-transformations-silver.md)). Pour être utilisées telles quelles (carte,
tableau de bord, futures tables de faits), il leur manque deux choses : la position
des aérogénérateurs n'existe qu'en Lambert-93, et chaque table ignore l'autre (un
aérogénérateur ne connaît pas le nom de son parc, un parc ne sait pas combien
d'aérogénérateurs sont réellement recensés).

## Décision

- Deux dimensions gold, sous les mêmes clés que le silver
  ([0003](0003-identifiant-logique-et-nom-physique.md)) :
  `wind_farm` → `venturi.gold.dim_wind_farm`,
  `wind_turbine` → `venturi.gold.dim_wind_turbine`
  ([0002](0002-nomenclature-des-tables.md)).
- Un pipeline gold lit les tables silver avec `read_table`, applique une fonction
  `transform` du même fichier (jointure puis un seul `select`, une ligne par colonne
  cible), et écrit avec `write_table` en annule et remplace.
- `dim_wind_turbine` garde le grain du silver et ajoute :
  - `longitude` / `latitude` en WGS84, calculées à partir de `x_lambert93` /
    `y_lambert93` par `utils/lambert93.py` (formules de l'IGN, en colonnes Spark) ;
  - les attributs du parc utiles à la lecture (`farm_name`, `farm_operating_state`,
    `farm_permit_status`, `farm_commissioning_date`).
- `dim_wind_farm` garde une ligne par parc et ajoute le résumé de ses
  aérogénérateurs : `located_turbine_count`, `located_capacity_mw`,
  `max_tip_height_m`, et le département, la région et le constructeur les plus
  représentés.
- Les jointures sont à gauche : aucune ligne du silver n'est perdue en gold.

## Conséquences

- `turbine_count` / `capacity_mw` (déclarés par le registre des parcs) et
  `located_turbine_count` / `located_capacity_mw` (recalculés) coexistent dans
  `dim_wind_farm`. Ils diffèrent pour quelques parcs : l'écart est une information,
  pas une erreur à corriger en gold.
- Un aérogénérateur dont le parc est absent du registre des parcs a ses colonnes
  `farm_*` à null ; un parc sans aérogénérateur recensé a
  `located_turbine_count` à 0.
- Si `farm_id` n'était pas unique en silver (cas non contrôlé, voir 0009), la
  jointure multiplierait les aérogénérateurs : ce contrôle reste à faire en recette.
- La conversion suppose que toutes les coordonnées sont en Lambert-93 (`epsg` =
  2154), comme le nom des colonnes silver.
- Les coordonnées sont en RGF93, assimilé au WGS84 : l'écart est inférieur au mètre.

## Alternatives écartées

- **`pyproj` dans une UDF** : une dépendance et une UDF Python pour une formule
  fermée d'une vingtaine de lignes.
- **Convertir les coordonnées en silver** : le silver reste une image typée de la
  source ; la position WGS84 est une donnée dérivée.
- **Une seule table dénormalisée** : les deux grains (parc, aérogénérateur) ont
  chacun leurs usages ; une table unique obligerait à dédoublonner pour compter
  les parcs.
