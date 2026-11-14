# Projet VENTURI
### Analyse des pertes de production éolienne et de leurs causes racines

> *En référence à l'effet Venturi, qui décrit comment un fluide accélère en passant dans un rétrécissement.*
> Note de cadrage – Expression de besoin fonctionnel

---

## 1. Fiche d'identité du projet

| Élément | Valeur |
|---|---|
| **Nom du projet** | VENTURI – Analyse des pertes de production éolienne et de leurs causes racines |
| **BU commanditaire** | Direction Exploitation & Maintenance – Pôle Performance des actifs éoliens |
| **Sponsor** | Responsable Performance du parc |
| **Utilisateurs principaux** | Ingénieurs performance, chefs d'équipe maintenance, asset managers |
| **Périmètre pilote** | Parc éolien de La Haute Borne (Meuse) – 4 turbines Senvion MM82 de 2 MW, mises en service en 2009 |
| **Type de traitement** | Micro-batch toutes les 10 minutes (rejeu de l'historique en flux) + batch quotidien et mensuel de reporting |
| **Nature du projet** | Data + IA : modèle de production attendue, intégré dans un pipeline de calcul d'indicateurs et d'analyse de causes racines |

---

## 2. Contexte métier

Un parc éolien ne produit jamais exactement ce qu'il devrait. Une partie de l'écart est normale (vent trop faible, arrêts programmés), mais une autre partie est une **perte évitable** : turbine mal orientée face au vent, réglage des pales dégradé, givre non détecté, bridage oublié, composant qui chauffe et fait baisser la puissance.

Aujourd'hui, le pôle Performance constate ces pertes **a posteriori**, lors du bilan mensuel, en comparant la production à la courbe de puissance théorique du constructeur. Cette méthode pose trois problèmes :

1. **Trop tardive** : une turbine désalignée peut perdre de l'énergie pendant des semaines avant d'être repérée.
2. **Trop grossière** : la courbe constructeur ne tient pas compte de la densité de l'air, de la turbulence, du vieillissement ou des effets de sillage entre turbines. Elle génère de fausses alertes et masque des pertes réelles.
3. **Non explicative** : le métier sait *combien* il a perdu, mais pas *pourquoi*. Les techniciens se déplacent sans diagnostic préalable.

---

## 3. Problématique et enjeux

**Problématique** : comment détecter au plus tôt les pertes de production évitables, les chiffrer en énergie et en euros, et en identifier la cause probable pour prioriser les interventions de maintenance ?

**Enjeux métier**

| Enjeu | Description |
|---|---|
| Financier | Chaque MWh non produit est un revenu perdu (vente sur le marché ou tarif d'obligation d'achat). Les pertes de quelques pourcents sur un parc se chiffrent vite en dizaines de milliers d'euros par an. |
| Maintenance | Passer d'une maintenance curative à une maintenance **conditionnelle** : intervenir avant la panne, avec le bon diagnostic et la bonne pièce. |
| Contractuel | Suivre la disponibilité garantie par le contrat de maintenance avec le turbinier, et disposer de preuves chiffrées en cas de litige. |
| Pilotage | Donner à l'asset manager une vision fiable de la performance réelle du parc, comparable d'une turbine à l'autre et d'un mois à l'autre. |

---

## 4. Acteurs et besoins

| Persona | Ce qu'il fait | Ce dont il a besoin |
|---|---|---|
| **Ingénieur performance** | Analyse la production, investigue les sous-performances | Une production attendue fiable par turbine, la liste des écarts anormaux et leur cause probable |
| **Chef d'équipe maintenance** | Planifie les interventions sur site | Une liste priorisée des turbines à inspecter, avec un diagnostic et une estimation de l'enjeu en euros |
| **Asset manager** | Suit la rentabilité du parc | Des indicateurs mensuels consolidés : énergie perdue, perte financière, disponibilité, tendance |
| **Direction Exploitation** | Arbitre les budgets de maintenance | Une vue synthétique des causes de pertes et de leur poids financier sur l'année |

---

## 5. Besoin fonctionnel

### 5.1 Exigences fonctionnelles

Priorisation MoSCoW : **M** = Must, **S** = Should, **C** = Could.

| ID | Exigence | Priorité |
|---|---|---|
| BF-01 | Calculer, pour chaque turbine et chaque pas de 10 minutes, la **production attendue** à partir des conditions réelles (vent, direction, température, densité de l'air). | M |
| BF-02 | Calculer l'**écart** entre production réelle et production attendue, et le convertir en énergie perdue (kWh) et en perte financière (€). | M |
| BF-03 | **Qualifier chaque période** : fonctionnement normal, arrêt, sous-performance, bridage, donnée invalide. | M |
| BF-04 | **Détecter les sous-performances anormales** persistantes (et non les simples fluctuations de vent) et lever une alerte. | M |
| BF-05 | Attribuer à chaque sous-performance une **cause racine probable** issue de la taxonomie (section 6), avec un niveau de confiance. | M |
| BF-06 | **Prioriser** les alertes par enjeu financier cumulé et par durée. | M |
| BF-07 | Produire un **reporting quotidien** par turbine et un **reporting mensuel** consolidé du parc (section 7). | M |
| BF-08 | Contrôler la **qualité des données** SCADA (valeurs manquantes, capteurs figés, valeurs hors bornes physiques) et exclure les périodes invalides des calculs. | M |
| BF-09 | **Comparer les turbines entre elles** : une turbine qui sous-performe alors que ses voisines non, dans les mêmes conditions de vent, est un signal fort. | S |
| BF-10 | Suivre la **dégradation lente** de la performance dans le temps (vieillissement, encrassement des pales). | S |
| BF-11 | Permettre à l'ingénieur performance de **valider ou corriger** la cause proposée, afin d'enrichir les données d'entraînement. | S |
| BF-12 | **Surveiller la dérive du modèle** et déclencher un réentraînement lorsque sa précision se dégrade. | S |
| BF-13 | Anticiper les **défaillances de composants** (multiplicateur, génératrice) à partir de la dérive des températures. | C |
| BF-14 | Générer automatiquement un **commentaire en langage naturel** résumant la performance du mois. | C |

### 5.2 Règles de gestion

- **RG-01** : la production attendue n'est calculée que lorsque le vent est dans la plage de fonctionnement de la turbine (entre la vitesse de démarrage et la vitesse de coupure).
- **RG-02** : une sous-performance n'est remontée en alerte que si l'écart dépasse un seuil (à calibrer, par exemple 5 % de l'attendu) pendant une durée minimale (par exemple 6 heures cumulées sur 24 heures), afin d'éviter les fausses alertes.
- **RG-03** : les périodes d'arrêt programmé (maintenance préventive) sont exclues du calcul de la perte évitable mais comptabilisées dans la disponibilité.
- **RG-04** : la perte financière est calculée avec le prix de l'électricité de l'heure correspondante (prix spot) ou, à défaut, avec un tarif de référence paramétrable.
- **RG-05** : le vent mesuré par l'anémomètre de nacelle étant perturbé par le rotor, toute comparaison inter-turbines utilise aussi un vent de référence indépendant (réanalyse météo).

### 5.3 User stories principales

- *En tant qu'ingénieur performance*, je veux voir chaque matin la liste des turbines en sous-performance avec leur cause probable, **afin de** lancer mes investigations sans analyser manuellement les données brutes.
- *En tant que chef d'équipe maintenance*, je veux connaître la perte en euros associée à chaque alerte, **afin de** prioriser les déplacements sur site.
- *En tant qu'asset manager*, je veux un bilan mensuel de l'énergie perdue par cause, **afin de** justifier les budgets de maintenance et suivre les engagements du turbinier.

---

## 6. Taxonomie des causes racines

Chaque cause est associée à une **signature** observable dans les données SCADA. C'est cette signature que le module de diagnostic doit reconnaître.

| Code | Cause racine | Signature dans les données | Action métier |
|---|---|---|---|
| RC-01 | **Désalignement en lacet** (la nacelle n'est pas face au vent) | Écart persistant entre direction du vent et orientation de la nacelle ; perte proportionnelle à l'angle | Recalibrer la girouette / le système d'orientation |
| RC-02 | **Anomalie d'angle de pales** | Angle de pales anormal pour la vitesse de vent ; perte en vent moyen | Contrôle du système de pitch |
| RC-03 | **Givrage** | Température extérieure proche de 0 °C, humidité, chute de production brutale à vent constant | Vérifier le système de détection de givre |
| RC-04 | **Bridage** (acoustique, chiroptères, réseau) | Puissance plafonnée à une valeur fixe, sur des plages horaires ou directions récurrentes | Vérifier que le bridage est justifié et bien paramétré |
| RC-05 | **Déclassement thermique** | Température d'un composant (multiplicateur, génératrice, roulements) élevée et en hausse avant la baisse de puissance | Inspection du composant, maintenance conditionnelle |
| RC-06 | **Dégradation lente** | Baisse progressive de l'indice de performance sur plusieurs mois, sans événement ponctuel | Inspection des pales (érosion, encrassement) |
| RC-07 | **Effet de sillage** | Sous-performance dépendant de la direction du vent, quand la turbine est derrière une voisine | Pas d'action corrective : perte structurelle à documenter |
| RC-08 | **Arrêt / indisponibilité** | Puissance nulle alors que le vent est suffisant | Analyse de l'arrêt (panne, maintenance, réseau) |
| RC-09 | **Problème capteur** | Anémomètre figé ou incohérent avec les turbines voisines et la réanalyse | Remplacement du capteur ; la perte est peut-être fictive |
| RC-00 | **Cause indéterminée** | Écart anormal sans signature reconnue | Investigation manuelle, puis étiquetage (BF-11) |

---

## 7. Indicateurs attendus

| Indicateur | Définition | Fréquence | Destinataire |
|---|---|---|---|
| Énergie produite (MWh) | Somme de la production réelle | Jour / mois | Tous |
| Énergie attendue (MWh) | Somme de la production prédite par le modèle | Jour / mois | Performance |
| **Énergie perdue (MWh)** | Attendue − produite, sur les périodes de fonctionnement valides | Jour / mois | Tous |
| **Perte financière (€)** | Énergie perdue × prix de l'heure | Jour / mois | Asset manager, direction |
| Indice de performance (%) | Produite / attendue | Jour / mois | Performance |
| Disponibilité temporelle (%) | Temps de fonctionnement / temps où le vent permet de produire | Mois | Asset manager |
| Disponibilité énergétique (%) | Énergie produite / (énergie produite + énergie perdue par indisponibilité) | Mois | Asset manager |
| **Répartition des pertes par cause** | Énergie et € perdus par code RC | Mois | Direction |
| Délai de détection | Temps entre le début d'une sous-performance et l'alerte | Mois | Performance |
| Taux d'alertes confirmées | Alertes validées par l'ingénieur / alertes émises | Mois | Équipe projet (qualité du modèle) |

---

## 8. Sources de données

### 8.1 Sources principales

| Source | Contenu | Granularité | Accès | Usage dans VENTURI |
|---|---|---|---|---|
| **SCADA La Haute Borne** (ENGIE Green) | Mesures des 4 turbines : puissance active et réactive, vitesse et direction du vent, orientation de la nacelle, angle des pales, vitesse du rotor, températures (extérieure, multiplicateur, génératrice, roulements) ; valeurs moyennes, min, max et écart-type | 10 minutes, 2013 à 2018 | Le portail open data historique d'ENGIE n'est plus en ligne. Une copie nettoyée 2013–2018 est publiée sur **Mendeley Data** (DOI 10.17632/vmyg4yp3s8). Un extrait est aussi fourni avec la librairie open source **OpenOA** (NREL), sur GitHub. Licence Ouverte Etalab 2.0. | Source centrale : entraînement du modèle, calcul des écarts, signatures des causes |
| **Réanalyses météo** (ERA5 de Copernicus, MERRA-2 de la NASA) | Vent, température, pression et densité de l'air sur une grille mondiale | Horaire | Gratuit après inscription (Copernicus Climate Data Store) ; extraits également fournis avec OpenOA | Vent de référence indépendant de l'anémomètre de nacelle (RG-05), calcul de la densité de l'air, détection des capteurs défaillants |
| **Prix de l'électricité** (ENTSO-E Transparency Platform) | Prix spot day-ahead de la zone France | Horaire | Gratuit après inscription, API disponible | Valorisation financière des pertes (RG-04) |
| **Fiche technique Senvion MM82** | Courbe de puissance constructeur, vitesses de démarrage et de coupure, puissance nominale | Statique | Documentation constructeur publique | Référence de base (baseline) à battre par le modèle, bornes physiques pour le contrôle qualité |

### 8.2 Source complémentaire de validation

| Source | Contenu | Accès | Usage |
|---|---|---|---|
| **SMARTEOLE** (ENGIE Green et NREL) | Données SCADA à 1 minute de 7 turbines, issues d'une campagne d'essais de pilotage du sillage, avec des désalignements volontaires | Zenodo, en accès ouvert | Valider la détection du désalignement (RC-01) et des effets de sillage (RC-07) sur un cas réel où la cause est connue |

### 8.3 Données internes non publiques (à simuler)

Dans un vrai projet, ces données viendraient des outils internes de l'exploitant. Elles ne sont pas publiques ; elles seront **générées de manière synthétique et réaliste** et clairement identifiées comme telles.

| Donnée | Système source en entreprise | Usage | Stratégie dans le projet |
|---|---|---|---|
| Journal des alarmes et codes d'état des turbines | SCADA / contrôleur turbine | Distinguer arrêts, pannes et bridages | Déduire les états à partir des signaux (puissance nulle, angle de pales en drapeau) |
| Historique des interventions de maintenance | GMAO | Exclure les arrêts programmés, étiqueter les causes | Générer un calendrier d'interventions plausible |
| Plans de bridage (acoustique, chiroptères) | Arrêté préfectoral, paramétrage turbine | Reconnaître les bridages légitimes | Déduire des plafonnements récurrents observés |
| **Incidents étiquetés** | Retours des techniciens | Entraîner et évaluer le classifieur de causes | **Injection contrôlée d'anomalies** dans les données réelles (désalignement, plafonnement, dérive thermique), dont la cause est donc connue |

### 8.4 Principales variables SCADA utilisées

Noms indicatifs, à valider à l'ouverture du jeu de données.

| Variable | Signification | Utilisée pour |
|---|---|---|
| `P_avg` | Puissance active moyenne | Cible du modèle, calcul des pertes |
| `Ws_avg` | Vitesse du vent (nacelle) | Variable explicative principale |
| `Wa_avg` | Direction absolue du vent | Sillage, désalignement |
| `Va_avg` | Angle entre vent et nacelle | Désalignement (RC-01) |
| `Ya_avg` | Orientation de la nacelle | Désalignement, sillage |
| `Ba_avg` | Angle des pales | Pitch (RC-02), arrêts, bridage |
| `Rs_avg` | Vitesse du rotor | Cohérence de fonctionnement |
| `Ot_avg` | Température extérieure | Givre (RC-03), densité de l'air |
| `Gb1t_avg`, `Gb2t_avg` | Températures des roulements du multiplicateur | Déclassement thermique (RC-05) |
| Variables `_std`, `_min`, `_max` | Écart-type et extrêmes sur 10 minutes | Turbulence, détection de capteurs figés |

---

## 9. Principe de la solution (vue fonctionnelle)

1. **Ingestion** : les données SCADA sont rejouées en flux, pas de 10 minutes par pas de 10 minutes, comme si elles arrivaient du parc en temps réel ; les sources externes (météo, prix) sont chargées en batch.
2. **Contrôle qualité** : filtrage des données invalides (BF-08).
3. **Modèle de production attendue** : entraîné hors ligne sur les périodes de fonctionnement normal, il prédit la puissance de chaque turbine à partir des conditions réelles (BF-01).
4. **Calcul des écarts et qualification** des périodes (BF-02, BF-03).
5. **Détection et diagnostic** : les écarts anormaux persistants deviennent des alertes ; un module combinant règles métier, explicabilité du modèle et classifieur entraîné sur les incidents étiquetés propose une cause racine (BF-04, BF-05).
6. **Restitution** : tables d'indicateurs, tableau de bord et liste d'alertes priorisées (BF-06, BF-07).

---

## 10. Périmètre

**Inclus**
- Les 4 turbines de La Haute Borne sur la période 2013–2018.
- Production attendue, pertes, diagnostic des causes, indicateurs et reporting.
- Suivi de la qualité du modèle et de sa dérive.

**Exclus**
- Pilotage des turbines (aucune action automatique sur le parc).
- Intégration avec un vrai outil de GMAO ou de ticketing.
- Prévision de production à plusieurs jours (sujet distinct : vente sur les marchés).

---

## 11. Critères d'acceptation

| Critère | Cible |
|---|---|
| Précision du modèle de production attendue | Erreur nettement inférieure à celle de la courbe constructeur sur les périodes de fonctionnement normal |
| Détection des anomalies injectées | Au moins 80 % des anomalies détectées (rappel), avec un taux de fausses alertes maîtrisé |
| Classification des causes | Cause correcte pour la majorité des anomalies injectées, matrice de confusion documentée |
| Délai de détection | Alerte levée en moins de 24 heures après le début d'une sous-performance |
| Traçabilité | Chaque indicateur recalculable à partir des données sources ; chaque alerte reliée aux données qui l'ont déclenchée |

---

## 12. Glossaire

| Terme | Définition |
|---|---|
| **SCADA** | Système de supervision qui enregistre les mesures des turbines, ici agrégées toutes les 10 minutes |
| **Courbe de puissance** | Relation entre vitesse du vent et puissance produite par une turbine |
| **Lacet (yaw)** | Rotation de la nacelle pour se placer face au vent |
| **Pitch** | Angle des pales, ajusté pour réguler la puissance |
| **Bridage** | Limitation volontaire de la production (bruit, protection des chauves-souris, contrainte réseau) |
| **Sillage** | Zone de vent ralenti et turbulent derrière une turbine, qui pénalise celles placées derrière |
| **Réanalyse** | Reconstitution météo historique combinant observations et modèles numériques |
| **GMAO** | Gestion de maintenance assistée par ordinateur |
| **Cause racine** | Origine réelle d'une sous-performance, au-delà du simple constat d'écart |
