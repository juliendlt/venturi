# 0012 – Agrégats gold par région et par département

- **Statut** : Proposée
- **Date** : 2026-11-21

## Contexte

La carte ([0011](0011-application-carte.md)) doit proposer une vue groupée :
région, puis département, puis parc, puis aérogénérateur, avec des chiffres clés à
chaque niveau (nombre de parcs et d'aérogénérateurs, puissance). Les deux niveaux
les plus fins existent déjà en gold ([0010](0010-dimensions-gold.md)) ; il manque
les deux niveaux territoriaux.

## Décision

- Deux agrégats gold, calculés à partir de `gold.wind_turbine`
  (`dim_wind_turbine`) :
  `wind_turbine_department` → `venturi.gold.agg_wind_turbine_department`,
  `wind_turbine_region` → `venturi.gold.agg_wind_turbine_region`
  ([0002](0002-nomenclature-des-tables.md) : `agg_`, grain en suffixe).
- Chaque agrégat est un `groupBy` suivi d'un `agg`, une ligne par indicateur :
  nombre de parcs et d'aérogénérateurs, puissance totale, part en exploitation,
  puissance moyenne, hauteur maximale, constructeur le plus représenté, centre
  (`longitude` / `latitude`) et emprise (`min_` / `max_`) des aérogénérateurs.
- Le territoire d'un aérogénérateur est celui de sa commune d'implantation
  (`department_code`, `region_code`).
- Les deux pipelines sont écrits séparément, sans fonction commune, même si leurs
  indicateurs sont les mêmes.
- La carte choisit le niveau selon le zoom : régions jusqu'au zoom 6, départements
  aux zooms 7 et 8, parcs aux zooms 9 et 10, aérogénérateurs à partir du zoom 11.

## Conséquences

- Ces pipelines lisent une table gold : ils se lancent après `gold.wind_turbine`.
- Un parc à cheval sur deux départements (ou deux régions) est compté dans
  `farm_count` de chacun : la somme des `farm_count` dépasse le nombre de parcs.
- La puissance d'un territoire est la somme des puissances des aérogénérateurs
  recensés, pas celle déclarée par les parcs.
- « En exploitation » est la valeur de la source, écrite dans le code des deux
  pipelines : si la source changeait ce libellé, les indicateurs
  `operating_*` tomberaient à zéro.
- Les tables ne portent que les codes : les noms des régions et des départements
  sont des libellés d'affichage, écrits dans la page de la carte.
- Sur la carte, le filtre par état du parc ne s'applique pas aux bulles des
  régions et des départements, qui viennent des agrégats.

## Alternatives écartées

- **Agréger dans le navigateur** : les indicateurs ne seraient ni recalculables ni
  réutilisables hors de la carte.
- **Un référentiel des régions et départements (source INSEE, bronze, silver)** :
  la bonne solution si les noms servent ailleurs que sur la carte ; trop pour
  cent libellés d'affichage.
- **Un seul agrégat avec une colonne de niveau** : deux grains dans une même table.
