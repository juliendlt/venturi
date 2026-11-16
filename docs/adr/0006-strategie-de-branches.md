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
- Une branche terminée est poussée sur GitHub et fusionnée dans `master` par une
  pull request, avec un commit de fusion (ni squash ni rebase), pour que chaque
  sujet reste visible dans l'historique.
- Une fois la pull request fusionnée, la branche est supprimée sur GitHub ; elle
  peut être conservée en local.
- Aucun commit ni aucune fusion ne se fait directement sur `master`.
- Les commits sont signés avec l'identité personnelle de l'auteur, configurée au
  niveau du dépôt et non de la machine.

## Conséquences

- Chaque sujet est isolé et relisible indépendamment.
- L'historique de `master` alterne commits de fusion et commits de branche.
- Chaque évolution laisse une pull request consultable sur GitHub, avec sa description.
- Les commits de fusion sont créés par GitHub, donc signés avec l'adresse `noreply`
  du compte et non avec l'adresse configurée dans le dépôt.
