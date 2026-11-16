# VENTURI – data prep

Préparation des données du projet VENTURI : analyse des pertes de production éolienne
et de leurs causes racines. Le besoin fonctionnel est décrit dans
`docs/projet_VENTURI_cadrage.md`.

Le projet est à son début : la structure, les données brutes et la configuration des
tables existent ; les pipelines restent à écrire.

## Commandes

Le projet est géré avec `uv` (Python >= 3.12).

```bash
uv sync                                        # installer l'environnement
uv add --package venturi-data-prep <paquet>    # ajouter une dépendance
cd src && uv run python -c "from venturi.config import load_tables; print(load_tables())"
```

Le package n'est pas installé dans l'environnement : le code s'exécute avec `src/`
comme racine des sources (`from venturi...`). Il n'y a pas encore de tests.

## Structure

```
config/tables.yaml          déclaration des tables, par zone
data/raw/                   fichiers bruts, versionnés
data/{bronze,silver,gold}/  sorties des pipelines, non versionnées
docs/                       note de cadrage et ADR (docs/adr/)
src/venturi/config.py       load_tables() : charge et valide tables.yaml
src/venturi/core/model/     modèles pydantic (TableModel, TablesModel)
src/venturi/core/exception/ exceptions du projet (vide)
src/venturi/pipeline/       pipelines par zone (vide)
src/venturi/utils/          utilitaires (vide)
```

## Configuration des tables

Toute table lue ou écrite par un pipeline est déclarée dans `config/tables.yaml` et
obtenue via `load_tables()` ; aucun nom de table n'est écrit en dur dans le code.

```python
tables = load_tables()
table = tables.bronze["wind_turbine"]
table.full_table_name   # venturi.bronze.oreol_aerogenerateur
table.schema_name       # bronze
```

- La clé du YAML (`wind_turbine`) est l'identifiant utilisé par le code : elle est
  stable. Le nom réel est dans `full_table_name` et se renomme dans le YAML seul.
- `full_table_name` suit `<catalogue>.<schéma>.<table>` (validé par pydantic).
- La même clé désigne la même entité d'une zone à l'autre.

## Conventions

- Nommage des tables : voir `docs/adr/0002-nomenclature-des-tables.md` avant d'en créer une.
- Rester simple : un modèle et un fichier de config tant qu'un second n'est pas
  nécessaire. Ne pas introduire de couche d'abstraction par anticipation.
- La config ne connaît ni l'environnement ni le service d'exécution (Databricks,
  Hive local) : cette adaptation appartient à une couche service, à venir.
- Code, commentaires, docstrings et messages de commit en français ; identifiants
  (tables, variables, fonctions) en anglais.
- Git : chaque évolution se fait sur une branche `feat/<sujet>`, fusionnée dans
  `master` par une pull request GitHub (commit de fusion). Jamais de commit direct
  sur `master`.

## Décisions d'architecture

Les décisions structurantes sont consignées dans `docs/adr/` (index dans
`docs/adr/README.md`). Toute nouvelle décision de ce type y ajoute un fichier
numéroté ; une décision remplacée est marquée comme telle, pas supprimée.
