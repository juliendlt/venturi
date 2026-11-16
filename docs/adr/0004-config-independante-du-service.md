# 0004 – Garder la config indépendante de l'environnement et du service

- **Statut** : Acceptée, complétée par [0008](0008-ecriture-des-tables-par-une-fonction.md)
- **Date** : 2026-11-14

## Contexte

Une version intermédiaire du chargeur composait le catalogue à partir de
l'environnement (`venturi_dev`, `venturi_stg`, `venturi_prd`, selon la variable
`VENTURI_ENV`). Le chargeur mélangeait alors deux responsabilités : décrire les
tables, et décider où elles vivent. Or la façon de résoudre un catalogue dépend du
service d'exécution (Databricks avec Unity Catalog, Hive en local, …), qui n'est
pas encore fixé.

## Décision

- La config des tables est purement déclarative : `load_tables()` lit le YAML et le
  valide, sans paramètre d'environnement ni variable d'environnement.
- `TableModel` porte le nom complet `full_table_name`
  (`<catalogue>.<schéma>.<table>`), dont le format est validé, et expose
  `catalog_name`, `schema_name` et `table_name`.
- L'adaptation au service et à l'environnement (catalogue réel, stockage) sera
  traitée dans une couche service dédiée, plus tard. *Mise à jour : cette adaptation
  est faite par la fonction `write_table`, et non par une couche dédiée ; voir
  [0008](0008-ecriture-des-tables-par-une-fonction.md).*

## Conséquences

- `config.py` n'a qu'une responsabilité et ne dépend d'aucun service.
- Une couche service pourra recomposer le nom à partir de `schema_name` et
  `table_name` avec son propre catalogue.
- En attendant, le catalogue `venturi` est écrit dans chaque entrée du YAML, et
  `table_path` est identique quel que soit l'environnement.

## Alternatives écartées

- **Catalogue `venturi_<env>` injecté par le chargeur** : mêle config et
  environnement, et fige le préfixe et la liste des environnements dans le code.
- **Fichier `environments.yaml`** : anticipe un besoin dont la forme dépend du
  service retenu.
