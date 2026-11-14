# 0002 – Nomenclature catalogue / schéma / table

- **Statut** : Acceptée
- **Date** : 2026-11-14

## Contexte

Les premiers noms (`schema_bronze.bronze_aerogenerator`) répétaient la zone dans le
schéma et dans la table, et mélangeaient français et anglais. Le projet vise une
nomenclature de niveau industriel, compatible avec un espace de noms à trois niveaux
(Unity Catalog).

## Décision

Nom complet d'une table : `<catalogue>.<schéma>.<table>`.

| Niveau | Règle | Exemples |
|---|---|---|
| Catalogue | le projet | `venturi` |
| Schéma | la zone | `bronze`, `silver`, `gold` |
| Table bronze | `<source>_<jeu de données>`, fidèle à la source | `oreol_aerogenerateur`, `oreol_parc` |
| Table silver | `<entité métier>` en anglais, sans mention de la source | `wind_turbine`, `wind_farm` |
| Table gold | `dim_` / `fact_` / `agg_`, grain en suffixe | `dim_turbine`, `fact_turbine_performance_10min`, `agg_turbine_performance_daily` |

Règles générales :

- `snake_case`, singulier, sans accents ;
- anglais partout, sauf le bronze qui garde le nom du jeu de données dans la source ;
- pas de préfixe de zone dans le nom de table : le schéma porte déjà l'information.

## Conséquences

- Le nom d'une table indique sa zone, et pour le bronze sa source.
- Les tables existantes ont été renommées :
  `schema_bronze.bronze_aerogenerator` → `venturi.bronze.oreol_aerogenerateur`,
  `schema_bronze.bronze_parc` → `venturi.bronze.oreol_parc`.
- Les exemples gold sont indicatifs : aucune table gold n'existe encore.

## Points laissés ouverts

- Les environnements `dev` / `stg` / `prd`, d'abord portés par le nom du catalogue
  (`venturi_<env>`), ont été sortis de la config : voir
  [0004](0004-config-independante-du-service.md).
- Des schémas techniques ont été évoqués (`landing` pour les fichiers bruts, `ml`
  pour les features et prédictions, `ops` pour la qualité et l'audit) mais ne sont
  pas retenus à ce stade.

## Alternatives écartées

- **Français partout** : écarté au profit de l'anglais pour les entités métier.
- **Catalogue par zone, schéma par source** : adapté à une plateforme multi-projets,
  disproportionné pour un projet unique.
