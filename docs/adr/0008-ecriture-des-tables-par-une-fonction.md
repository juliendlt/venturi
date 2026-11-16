# 0008 – Adapter l'écriture au service par une simple fonction

- **Statut** : Acceptée
- **Date** : 2026-11-16

## Contexte

L'[ADR 0004](0004-config-independante-du-service.md) renvoyait l'adaptation au
service d'exécution (catalogue réel, stockage) à une « couche service, à venir ».
Une première version de cette couche (classe abstraite `Service`, implémentations
locale et Databricks, objet `Lakehouse`, option `--service`, réenregistrement des
tables au démarrage) s'est révélée disproportionnée : le seul vrai écart entre les
deux services porte sur le nom et l'emplacement de la table au moment d'écrire.

## Décision

- Une seule fonction, `write_table(df, table, mode)` dans
  `core/commons/writer.py`, crée le schéma s'il n'existe pas puis écrit la table
  Delta :
  - sur Databricks (`DATABRICKS_RUNTIME_VERSION` défini), la table est managée par
    Unity Catalog sous `full_table_name` ;
  - en local, Spark ne connaît pas le catalogue `venturi` : la table s'appelle
    `<schéma>.<table>` et ses données sont stockées à `table_path`, sous la racine
    du projet.
- La session Spark est créée par `build_spark()` dans `core/spark.py` : la session
  existante sur Databricks, sinon Spark local avec Delta.
- Les chemins de fichiers de la landing sont résolus par
  `project_root / file_path`. Un chemin absolu (`/Volumes/...`) reste tel quel.

## Conséquences

- La config reste indépendante du service ([0004](0004-config-independante-du-service.md)) :
  la différence entre local et Databricks tient dans une condition de
  `write_table`.
- Le catalogue en mémoire du Spark local est vide à chaque lancement : une table
  écrite lors d'un lancement précédent n'est pas lisible par son nom, seulement par
  son chemin (`table_path`).
- `databricks-connect` n'est pas pris en charge : hors runtime Databricks, le code
  tourne toujours en local.

## Alternatives écartées

- **Couche service (classe `Service` et `Lakehouse`)** : écartée, trop
  d'abstraction pour un seul point de variation. On pourra y revenir si les écarts
  entre services se multiplient.
- **Tables managées en local** : le dossier de l'entrepôt subsiste d'un lancement à
  l'autre alors que le catalogue en mémoire est vide, ce qui fait échouer la
  recréation de la table.
