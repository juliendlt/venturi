# 0006 – Structure sur `master`, évolutions sur des branches dédiées

- **Statut** : Acceptée
- **Date** : 2026-11-14

## Contexte

Le projet est un projet de portfolio, hébergé sur un dépôt GitHub personnel.
L'historique doit rester lisible : on veut distinguer le socle du projet de chaque
évolution fonctionnelle.

## Décision

- `master` porte la structure du projet (premier commit : squelette du package,
  données brutes, arborescence des zones, note de cadrage).
- Chaque évolution se fait sur une branche `feat/<sujet>` ; la première est
  `feat/tables-config` (configuration des tables).
- Une branche terminée est fusionnée dans `master` par un commit de fusion
  (`git merge --no-ff`), pour que chaque sujet reste visible dans l'historique.
- Les commits sont signés avec l'identité personnelle de l'auteur, configurée au
  niveau du dépôt et non de la machine.

## Conséquences

- Chaque sujet est isolé et relisible indépendamment.
- L'historique de `master` alterne commits de fusion et commits de branche.
- Pas de pull request à ce stade : la fusion est faite en local puis poussée.
