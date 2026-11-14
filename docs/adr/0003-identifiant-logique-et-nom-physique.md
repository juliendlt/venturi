# 0003 – Séparer l'identifiant logique du nom physique d'une table

- **Statut** : Acceptée
- **Date** : 2026-11-14

## Contexte

Une première version de `tables.yaml` utilisait le nom physique de la table comme
clé. Le code accédait donc aux tables par leur nom réel
(`tables.bronze["oreol_aerogenerateur"]`) : renommer une table obligeait à modifier
le code, ce qui est inacceptable pour un projet industriel.

## Décision

- La clé d'une table dans le YAML est un **identifiant logique**, stable, utilisé
  par le code (`wind_turbine`).
- Le **nom physique** est un champ de la table (`full_table_name`) et ne sert jamais
  de clé.
- La même clé logique désigne la même entité d'une zone à l'autre :
  `bronze.wind_turbine` et `silver.wind_turbine`.

```yaml
bronze:
  wind_turbine:
    full_table_name: venturi.bronze.oreol_aerogenerateur
```

## Conséquences

- Renommer un catalogue, un schéma ou une table se fait dans le YAML, sans toucher au code.
- On suit une entité de zone en zone avec le même identifiant.
- Renommer une clé logique reste une modification de code : elle doit être choisie
  pour durer.

## Alternatives écartées

- **Nom physique en clé** : couple le code au nommage (voir le contexte).
- **Modèles séparés « définition » / « table résolue » avec un fichier
  `environments.yaml`** : découplage complet mais trois modèles et deux fichiers
  pour quatre tables ; jugé trop complexe.
