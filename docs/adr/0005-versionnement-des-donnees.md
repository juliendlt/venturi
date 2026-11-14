# 0005 – Versionner les données brutes et l'arborescence des zones

- **Statut** : Acceptée
- **Date** : 2026-11-14

## Contexte

Le dossier `data/` contient les fichiers bruts et recevra les sorties des pipelines
(bronze, silver, gold). Les sorties sont régénérables et volumineuses ; les fichiers
bruts sont le point de départ nécessaire pour rejouer le projet.

## Décision

- `data/raw/` est versionné avec ses fichiers (registre OREOL : `aerogenerator.csv`,
  `parc.csv`, environ 4,4 Mo).
- Les autres dossiers de `data/` sont versionnés pour leur arborescence seulement,
  via un fichier `.gitkeep` ; tout autre fichier y est ignoré, y compris dans de
  futurs sous-dossiers.

```gitignore
/data/**
!/data/**/
!/data/raw/**
!/data/**/.gitkeep
```

## Conséquences

- Un clone du dépôt suffit pour lancer les pipelines, sans téléchargement préalable.
- Les sorties des pipelines ne polluent pas l'historique.
- Un nouveau dossier de zone doit recevoir un `.gitkeep` pour apparaître dans le dépôt.
- Cette approche ne tient que pour de petits fichiers bruts : les sources
  volumineuses à venir (SCADA, réanalyses météo) devront rester hors du dépôt.

## Alternatives écartées

- **Ignorer tout `data/`** : le projet n'est plus rejouable après un clone.
- **Tout versionner** : historique alourdi par des données régénérables.
