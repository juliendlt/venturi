# VENTURI – data prep

Préparation des données du projet VENTURI : analyse des pertes de production éolienne
et de leurs causes racines. Le besoin fonctionnel est décrit dans
`docs/projet_VENTURI_cadrage.md`.

Le projet est à son début : la structure, les données brutes et la configuration des
tables existent, ainsi que le point d'entrée, les pipelines bronze, silver et gold
du registre OREOL (parcs, aérogénérateurs) et une application de carte. Les données
SCADA, météo et prix du cadrage restent à intégrer.

## Commandes

Le projet est géré avec `uv` (Python >= 3.12).

```bash
uv sync                                        # installer l'environnement
uv add --package venturi-data-prep <paquet>    # ajouter une dépendance
uv run venturi --list                          # pipelines disponibles
uv run venturi bronze.wind_farm                # lancer un pipeline
uv run venturi-map                             # carte interactive (lit les tables gold)
```

`uv sync` installe le package `venturi` en mode éditable, avec la commande `venturi`
(`src/venturi/main.py`) et la commande `venturi-map` (`src/venturi/app/server.py`). Spark 4 demande Java 17 ou 21. Il n'y a pas encore de tests.

## Pipelines

- Un pipeline hérite de `Pipeline` (`src/venturi/pipeline/base.py`) : un `name`
  (`<zone>.<identifiant logique>`), une `description`, une méthode `run(context)`.
- Pour le rendre exécutable, l'ajouter à la liste de
  `src/venturi/pipeline/registry.py`. Pas de chargement par réflexion.
- Un pipeline ne crée ni session Spark ni logger : il reçoit un `Context`
  (`spark`, `tables`, `logger`, `project_root`) construit par le point d'entrée.
- Les lectures et écritures passent par `core/commons/reader.py` et `writer.py`,
  avec les options typées de `core/commons/options.py`. Une table de `tables.yaml`
  s'écrit avec `write_table(df, table, mode)` (ADR 0008).
- Un CSV bronze se lit avec son schéma déclaré dans `src/venturi/schema/bronze/`
  (ADR 0007).
- Un pipeline silver lit la table bronze de même clé avec `read_table(spark, table)`
  et la transforme par une fonction `transform(bronze)` : un seul `select`, une
  ligne par colonne cible, colonnes en anglais, `cast` strict (ADR 0009).
- Un pipeline gold lit les tables silver avec `read_table` et les transforme par une
  fonction `transform` : jointure à gauche, puis un seul `select` (ADR 0010).
- Les agrégats gold par département et par région lisent `gold.wind_turbine`
  (ADR 0012).
- Ordre de lancement : bronze, puis silver, puis gold, pour `wind_farm` et
  `wind_turbine` ; enfin `gold.wind_turbine_department` et
  `gold.wind_turbine_region`.
- La session Spark est créée uniquement dans `src/venturi/core/spark.py`.

## Structure

```
config/tables.yaml          déclaration des tables, par zone
data/raw/                   fichiers bruts, versionnés
data/{bronze,silver,gold}/  sorties des pipelines, non versionnées
docs/                       note de cadrage et ADR (docs/adr/)
src/venturi/main.py         point d'entrée : arguments, contexte, lancement du pipeline
src/venturi/config.py       load_tables() : charge et valide tables.yaml
src/venturi/core/context.py Context transmis aux pipelines
src/venturi/core/spark.py   création de la session Spark
src/venturi/core/commons/   readers, writers et options Spark
src/venturi/core/model/     modèles pydantic (TableModel, TablesModel)
src/venturi/schema/         schémas StructType par zone, sous la clé de tables.yaml
src/venturi/app/            carte interactive : serveur HTTP et page Leaflet (ADR 0011)
src/venturi/pipeline/       Pipeline, registre, pipelines par zone
src/venturi/utils/          utilitaires (conversion Lambert-93 -> WGS84)
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
  Hive local) : cette adaptation se limite à `write_table` (ADR 0008).
- Schémas Spark : un `StructField` écrit par colonne, jamais généré par une boucle ;
  tout en `StringType` en bronze (ADR 0007).
- Code, commentaires, docstrings et messages de commit en français ; identifiants
  (tables, variables, fonctions) en anglais.
- Git : chaque évolution se fait sur une branche `feat/<sujet>`, fusionnée dans
  `master` par une pull request GitHub (commit de fusion). Jamais de commit direct
  sur `master`. Les pull requests se créent et se fusionnent avec la CLI `gh`
  (`gh pr create --base master`, puis `gh pr merge <n> --merge`), branche distante
  supprimée ensuite (ADR 0006).

## Décisions d'architecture

Les décisions structurantes sont consignées dans `docs/adr/` (index dans
`docs/adr/README.md`). Toute nouvelle décision de ce type y ajoute un fichier
numéroté ; une décision remplacée est marquée comme telle, pas supprimée.
