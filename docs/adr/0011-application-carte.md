# 0011 – Application de carte : serveur standard et page Leaflet

- **Statut** : Proposée
- **Date** : 2026-11-21

## Contexte

Les dimensions gold ([0010](0010-dimensions-gold.md)) doivent être consultables sur
une carte interactive : un point par parc à l'échelle du pays, puis les
aérogénérateurs du parc quand on zoome.

## Décision

- L'application vit dans le package, `src/venturi/app/`, et se lance par la
  commande `venturi-map` (`uv run venturi-map`).
- Au démarrage, elle lit `gold.wind_farm` et `gold.wind_turbine` avec `read_table`
  (les tables viennent de `load_tables()`, aucun nom en dur), garde le résultat en
  mémoire sous forme de JSON, puis arrête Spark.
- Le serveur est `http.server` de la bibliothèque standard : la page (`/`) et deux
  routes de données (`/api/farms`, `/api/turbines`). Il n'écoute que sur
  `127.0.0.1`.
- La carte est une page HTML unique (`static/index.html`) avec Leaflet, chargé
  depuis un CDN, et un fond OpenStreetMap. En dessous du zoom 11, un point par
  parc ; à partir du zoom 11, les aérogénérateurs de la zone affichée, avec le nom
  de leur parc.

## Conséquences

- Aucune dépendance Python ajoutée.
- Le démarrage prend le temps d'une session Spark (quelques dizaines de secondes) ;
  ensuite la carte ne dépend plus de Spark.
- Les données sont figées au démarrage : après un nouveau lancement des pipelines
  gold, il faut relancer l'application.
- Leaflet et les tuiles viennent d'Internet : la carte ne s'affiche pas hors ligne.
- L'application lit les tables comme un pipeline local (`table_path`) ; elle n'est
  pas prévue pour être déployée telle quelle (Databricks Apps, serveur partagé).

## Alternatives écartées

- **Streamlit ou Dash** : une dépendance lourde, et l'affichage dépendant du zoom
  y demande de toute façon du JavaScript.
- **Lire Delta sans Spark (`deltalake`)** : démarrage instantané, mais une seconde
  façon de lire les tables à côté de `read_table`. À reconsidérer si le temps de
  démarrage gêne.
- **Exporter un fichier GeoJSON par un pipeline** : un produit de plus à maintenir,
  hors des tables déclarées dans `tables.yaml`.
