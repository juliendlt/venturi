# VENTURI – data prep

Préparation des données du projet **VENTURI** : analyse des pertes de production
éolienne et de leurs causes racines. Le besoin fonctionnel est décrit dans la
[note de cadrage](docs/projet_VENTURI_cadrage.md).

Les données suivent une architecture en médaillon :

| Zone | Rôle | État |
|---|---|---|
| `bronze` | Copie fidèle des sources, toutes colonnes en chaîne | registre OREOL (parcs, aérogénérateurs) |
| `silver` | Données typées et nettoyées, par entité métier | `wind_farm`, `wind_turbine` |
| `gold` | Tables d'analyse (dimensions, faits, agrégats) | `dim_wind_farm`, `dim_wind_turbine`, `agg_wind_turbine_department`, `agg_wind_turbine_region` |

## Prérequis

- [uv](https://docs.astral.sh/uv/) et Python 3.12 ou plus
- Java 17 ou 21 (Spark 4)

## Démarrage

```bash
uv sync                          # installe l'environnement et la commande venturi
uv run venturi --list            # pipelines disponibles
uv run venturi bronze.wind_farm  # lance un pipeline
```

Pour alimenter toutes les tables puis ouvrir la carte des parcs :

```bash
uv run venturi bronze.wind_farm && uv run venturi bronze.wind_turbine
uv run venturi silver.wind_farm && uv run venturi silver.wind_turbine
uv run venturi gold.wind_farm   && uv run venturi gold.wind_turbine
uv run venturi gold.wind_turbine_department && uv run venturi gold.wind_turbine_region
uv run venturi-map               # http://127.0.0.1:8050/
```

La carte est une vue groupée : une bulle par région, puis par département, puis un
point par parc, puis les aérogénérateurs, selon le zoom. Chaque niveau affiche ses
chiffres clés (parcs, aérogénérateurs, puissance) et un clic descend au suivant.

En local, Spark tourne sur le poste avec Delta et les tables sont écrites sous
`data/<zone>/`. Sur un runtime Databricks, elles sont écrites dans Unity Catalog
sous leur nom complet (`venturi.bronze.wind_farm`, …).

## Organisation

```
config/tables.yaml     tables du projet, par zone
config/landing.yaml    fichiers bruts, par source
data/raw/              fichiers bruts (versionnés)
docs/adr/              décisions d'architecture
src/venturi/
  main.py              point d'entrée de la commande venturi
  app/                 carte interactive (commande venturi-map)
  core/                session Spark, contexte, readers et writers, modèles
  schema/              schémas Spark déclarés, par zone
  pipeline/            pipelines, par zone, et leur registre
```

## Ajouter un pipeline

1. Déclarer la table dans `config/tables.yaml`, en suivant la
   [nomenclature](docs/adr/0002-nomenclature-des-tables.md).
2. Pour une source brute, déclarer le fichier dans `config/landing.yaml` et son
   schéma dans `src/venturi/schema/`.
3. Écrire une classe héritant de `Pipeline` dans `src/venturi/pipeline/<zone>/`,
   qui écrit avec `write_table`.
4. L'ajouter au registre `src/venturi/pipeline/registry.py`.

## Contribuer

Chaque évolution se fait sur une branche `feat/<sujet>` et est fusionnée dans
`master` par une pull request, avec un commit de fusion. Les pull requests passent
par la [CLI GitHub](https://cli.github.com/) :

```bash
git push -u origin feat/<sujet>
gh pr create --base master --title "<titre>" --body "<description>"
gh pr merge <numéro> --merge
git push origin --delete feat/<sujet>
```

Les décisions structurantes sont consignées dans [docs/adr](docs/adr/README.md).
