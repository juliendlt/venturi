# 0009 – Règles des transformations silver

- **Statut** : Proposée
- **Date** : 2026-11-18

## Contexte

Le bronze conserve les registres OREOL tels que la source les livre : colonnes en
chaîne, noms français, une ligne par parc et par commune pour les parcs
([0007](0007-schemas-bronze-en-chaine.md)). Les tables silver `wind_farm` et
`wind_turbine` doivent être typées et utilisables telles quelles par le gold.

## Décision

- Un pipeline silver lit la table bronze de même clé avec `read_table`, applique une
  fonction `transform(bronze)` du même fichier, puis écrit avec `write_table` en
  annule et remplace.
- `transform` est un seul `select` : une ligne par colonne cible, qui porte le
  renommage, la conversion et le nettoyage de cette colonne.
- Les colonnes sont renommées en anglais, avec des noms courts ; les valeurs
  (états, statuts) restent celles de la source.
- Seules les colonnes utiles à l'analyse sont gardées en silver ; les autres
  restent disponibles en bronze.
- Les conversions sont strictes : `cast`, en mode ANSI (défaut de Spark 4). Une
  valeur qui ne se convertit pas fait échouer le pipeline, comme une ligne
  malformée en bronze (`FAILFAST`).
- Nettoyages appliqués : espaces de bord retirés sur les libellés libres,
  constructeur en majuscules.
- `silver.wind_farm` a une ligne par parc : les colonnes de commune, seules à varier
  pour un même parc, sont retirées et les lignes dédoublonnées. Sont aussi écartés
  l'exploitant (raison sociale, SIRET, en grande partie anonymisés), les dates
  intermédiaires de la procédure, le renouvellement et `geom_wgs84_point`,
  redondant avec `longitude` / `latitude`.
- `silver.wind_turbine` garde le grain du bronze. Sont écartés les attributs du
  parc recopiés par la source (nom, état, statut), le balisage lumineux et `epsg`,
  toujours égal à 2154 : les coordonnées s'appellent `x_lambert93` / `y_lambert93`.

## Conséquences

- La liste des communes d'un parc n'est plus dans `silver.wind_farm` : elle se
  retrouve par les aérogénérateurs, ou dans le bronze.
- L'unicité de `farm_id` n'est pas contrôlée par le pipeline : si une colonne
  gardée variait pour un même parc, le dédoublonnage laisserait plusieurs lignes.
  Ce contrôle relève de la recette.
- Si la source livrait un autre système de coordonnées que Lambert-93, le nom
  `x_lambert93` deviendrait faux : `epsg` est à contrôler en recette.
- Une valeur mal formée dans une nouvelle livraison bloque le silver jusqu'à
  correction de la règle de conversion.
- Les valeurs aberrantes mais convertibles sont conservées (date de dépôt en l'an
  0004, puissance unitaire de 87 MW, constructeur « A déterminer ») : leur
  traitement relève d'un contrôle qualité à définir.
- Il n'y a pas de schéma silver déclaré à part : le `select` de `transform` en tient
  lieu.

## Alternatives écartées

- **`try_cast`** : une valeur invalide devient null sans que personne ne le voie.
- **Garder le grain parc × commune en silver** : toute somme de puissance ou de
  nombre d'aérogénérateurs compterait plusieurs fois les parcs à plusieurs communes.
- **Communes d'un parc dans une colonne tableau** : plus complexe, sans usage
  identifié à ce stade.
