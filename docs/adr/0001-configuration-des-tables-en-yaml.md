# 0001 – Déclarer les tables dans un YAML validé par pydantic

- **Statut** : Acceptée
- **Date** : 2026-11-14

## Contexte

Les pipelines vont lire et écrire des tables dans plusieurs zones (bronze, silver,
gold). Sans référentiel commun, les noms et emplacements des tables se retrouvent
écrits en dur et dupliqués dans le code.

## Décision

- Toutes les tables sont déclarées dans un fichier unique, `config/tables.yaml`,
  organisé par zone.
- Le fichier est chargé par `load_tables()` (`src/venturi/config.py`) et validé par
  deux modèles pydantic (`src/venturi/core/model/table_model.py`) :
  - `TableModel` : une table (`full_table_name`, `table_path`, `version`,
    `write_checkpoint`) ;
  - `TablesModel` : les tables par zone (`bronze`, `silver`, `gold`).
- `TablesModel` refuse toute zone inconnue (`extra="forbid"`), pour détecter les
  fautes de frappe au chargement.
- Le chemin du YAML est calculé depuis l'emplacement de `config.py`, donc
  indépendant du répertoire d'exécution.

## Conséquences

- Un seul endroit à modifier pour ajouter, renommer ou déplacer une table.
- Une config invalide échoue au chargement, avec une erreur rattachée au champ fautif.
- Ajouter une zone demande d'ajouter un champ à `TablesModel`.
- Dépendances ajoutées : `pydantic`, `pyyaml`.
- Le fichier est relu à chaque appel de `load_tables()` (pas de cache).

## Alternatives écartées

- **Noms de tables en constantes Python** : pas de séparation entre configuration et code.
- **Un fichier par zone** : inutile au volume actuel.
