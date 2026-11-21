# Décisions d'architecture (ADR)

Chaque fichier consigne une décision structurante : son contexte, ce qui a été
décidé, ses conséquences et les alternatives écartées.

| N° | Décision | Statut | Date |
|---|---|---|---|
| [0001](0001-configuration-des-tables-en-yaml.md) | Déclarer les tables dans un YAML validé par pydantic | Acceptée | 2026-11-14 |
| [0002](0002-nomenclature-des-tables.md) | Nomenclature catalogue / schéma / table | Acceptée | 2026-11-14 |
| [0003](0003-identifiant-logique-et-nom-physique.md) | Séparer l'identifiant logique du nom physique d'une table | Acceptée | 2026-11-14 |
| [0004](0004-config-independante-du-service.md) | Garder la config indépendante de l'environnement et du service | Acceptée, complétée par 0008 | 2026-11-14 |
| [0005](0005-versionnement-des-donnees.md) | Versionner les données brutes et l'arborescence des zones | Acceptée | 2026-11-14 |
| [0006](0006-strategie-de-branches.md) | Structure sur `master`, évolutions sur des branches dédiées | Acceptée | 2026-11-14 |
| [0007](0007-schemas-bronze-en-chaine.md) | Schémas bronze déclarés en Python, toutes colonnes en chaîne | Acceptée | 2026-11-16 |
| [0008](0008-ecriture-des-tables-par-une-fonction.md) | Adapter l'écriture au service par une simple fonction | Acceptée | 2026-11-16 |
| [0009](0009-transformations-silver.md) | Règles des transformations silver | Proposée | 2026-11-18 |
| [0010](0010-dimensions-gold.md) | Dimensions gold des parcs et des aérogénérateurs | Proposée | 2026-11-21 |
| [0011](0011-application-carte.md) | Application de carte : serveur standard et page Leaflet | Proposée | 2026-11-21 |
| [0012](0012-agregats-gold-par-territoire.md) | Agrégats gold par région et par département | Proposée | 2026-11-21 |

## Ajouter une décision

1. Créer `NNNN-titre-court.md` avec le numéro suivant, sur le modèle des fichiers existants.
2. Ajouter la ligne correspondante dans le tableau ci-dessus.
3. Si elle remplace une décision existante, passer l'ancienne au statut
   « Remplacée par NNNN » sans la supprimer.
