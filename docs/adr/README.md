# Décisions d'architecture (ADR)

Chaque fichier consigne une décision structurante : son contexte, ce qui a été
décidé, ses conséquences et les alternatives écartées.

| N° | Décision | Statut | Date |
|---|---|---|---|
| [0001](0001-configuration-des-tables-en-yaml.md) | Déclarer les tables dans un YAML validé par pydantic | Acceptée | 2026-11-14 |
| [0002](0002-nomenclature-des-tables.md) | Nomenclature catalogue / schéma / table | Acceptée | 2026-11-14 |
| [0003](0003-identifiant-logique-et-nom-physique.md) | Séparer l'identifiant logique du nom physique d'une table | Acceptée | 2026-11-14 |
| [0004](0004-config-independante-du-service.md) | Garder la config indépendante de l'environnement et du service | Acceptée | 2026-11-14 |
| [0005](0005-versionnement-des-donnees.md) | Versionner les données brutes et l'arborescence des zones | Acceptée | 2026-11-14 |
| [0006](0006-strategie-de-branches.md) | Structure sur `master`, évolutions sur des branches dédiées | Acceptée | 2026-11-14 |

## Ajouter une décision

1. Créer `NNNN-titre-court.md` avec le numéro suivant, sur le modèle des fichiers existants.
2. Ajouter la ligne correspondante dans le tableau ci-dessus.
3. Si elle remplace une décision existante, passer l'ancienne au statut
   « Remplacée par NNNN » sans la supprimer.
