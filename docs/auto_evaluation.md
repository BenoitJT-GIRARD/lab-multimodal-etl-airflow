# Fiche d'auto-évaluation

**Projet n°12 — Extrayez des données multimodales de sites web**
**Auteur :** Benoit Girard

Chaque indicateur de réussite est coché et documenté par l'artefact correspondant.

## Extraire des données issues de toutes sources confondues

### Rapport d'exploration de sources

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon rapport est structuré avec des sections claires. | `docs/rapport_exploration_sources.md`, 7 sections. |
| ☑ | J'ai utilisé le format attendu : Markdown ou PDF. | Markdown. |
| ☑ | J'ai collecté des données d'au moins 3 sources différentes. | **4 sources intégrées**, par 4 méthodes d'accès distinctes : flux RSS (3 éditeurs), API NewsData.io, dépôt GitHub FakeNewsNet, jeu Kaggle Fakeddit. |
| ☑ | J'ai identifié et décrit des formats adaptés au traitement/stockage. | §6 : JSON + fichiers image pour le brut, Parquet pour le jeu transformé, base relationnelle pour le stockage — chaque choix argumenté. |

### Scripts d'extraction automatisée

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon script s'exécute sans intervention manuelle. | `scripts/run_extraction.py` ; `collecte_sources()` enchaîne les 4 connecteurs. |
| ☑ | Mon code est structuré en fonctions claires. | Un module par source dans `src/checkitai/sources/`, chacun exposant une fonction `fetch_*` ; téléchargement des images isolé dans `images.py`. |
| ☑ | Mon script gère les erreurs et j'utilise des logs. | `try/except` par source, délais d'attente réseau, `logging` centralisé (`logging_setup.py`). Une source en panne est comptée et n'interrompt pas les autres — testé (`tests/test_extract.py`). |
| ☑ | Les données extraites sont cohérentes avec mon cas d'usage. | Chaque publication porte un texte **et un fichier image téléchargé et validé**. Déroulé dans `notebooks/02_extraction.ipynb`. |

## Transformer des données afin de les adapter à leur utilisation finale

### Pipeline de transformation reproductible

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon script fonctionne sans erreur à partir des données extraites. | `scripts/run_transformation.py`, `src/checkitai/transform.py`. |
| ☑ | Mon pipeline est divisé en étapes claires. | `lit_brut` → `traite` → `exporte`, et des fonctions unitaires (`nettoie_texte`, `valide_image`, `normalise_date`, `normalise_label`). |
| ☑ | J'ai inclus des logs pour tracer chaque transformation. | Publications lues, retenues, doublons retirés, fichiers exportés. |
| ☑ | J'ai utilisé des paramètres configurables. | `TransformConfig` (longueur minimale de texte, image obligatoire, format de sortie) ; `ExtractionConfig` et `ImageConfig` sont également surchargeables par variables d'environnement. |

### Schéma de données finalisé

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon schéma est lisible : champs et types bien définis. | `docs/schema_donnees.mmd` (+ PNG et PDF) et le dictionnaire `docs/schema_donnees.md`, tous deux générés depuis `src/checkitai/schema.py`. |
| ☑ | J'ai inclus texte, images, métadonnées utiles. | Entités CONTENU_TEXTE, CONTENU_IMAGE, SOURCE, LABEL et PUBLICATION ; chaque champ porte son rôle (NLP, VISION, TARGET, METADATA, KEY). |
| ☑ | Mon schéma garantit le lien entre texte et image. | Relations `1—1` PUBLICATION↔CONTENU_TEXTE et PUBLICATION↔CONTENU_IMAGE, champ `image_path` (le fichier réel) et `has_image`. Trois contrôles successifs, détaillés au §4 du schéma. |

## Charger des données afin de les stocker dans un emplacement adapté

### Flux ETL (Airflow)

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon DAG s'exécute sans erreur dans Airflow. | Airflow 2.10.4 : 5 tâches en `SUCCESS`, `DagRun state=success`, 114 publications chargées. Journaux dans `docs/preuve_execution_airflow.md`. |
| ☑ | Mes tâches sont bien séparées. | 5 `PythonOperator` : `extraction` → `transformation` → `chargement` → `metriques` → `nettoyage`. Elles s'échangent leurs résultats par fichiers, jamais par XCom : **chacune est relançable seule**, preuve à l'appui (§3 de la preuve d'exécution). |

## Définir des indicateurs de performance pertinents

### Tableau de bord KPI de l'ETL

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Le tableau est lisible, interactif, visualisations étiquetées. | `dashboard/app.py` (Streamlit + Plotly) et `notebooks/04_kpi.ipynb`. |
| ☑ | Les KPI mesurent les points critiques du pipeline. | Qualité (validité, association texte-image, images réellement obtenues), volume et diversité (concentration des sources), fraîcheur (âge médian), performance et coût (durée par étape, débit, quota d'API, disque). |
| ☑ | Le tableau est compréhensible même par des non-techniciens. | Chaque carte porte une phrase expliquant ce qu'elle mesure ; les seuils sont traduits en feux vert / orange / rouge ; une galerie d'images montre concrètement ce que le pipeline produit. |

### Plan de monitoring

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon plan est clair et bien structuré. | `docs/plan_monitoring.md`, 9 sections. |
| ☑ | Il couvre seuils d'alerte, gestion des erreurs, rythmes de vérification. | Seuils au §3 — définis dans le code et lus par le tableau de bord, donc jamais désynchronisés du document. Gestion des erreurs au §4, fréquences au §5. |
| ☑ | Mon plan est cohérent avec le contexte professionnel. | Aligné sur le besoin CheckItAI (fraîcheur, fiabilité, sécurité de la base) et prolongé par une section sur l'industrialisation, Databricks ou Kubernetes. |

---

## Points de discussion

**Ce qui a été le plus difficile.** Rendre les tâches Airflow réellement indépendantes. La
version initiale passait les chemins de fichiers par XCom, ce qui paraissait naturel mais
enchaînait les tâches : impossible de rejouer la transformation seule. Il a fallu
repenser le passage de relais sous forme de fichiers, avec un repli sur le dernier
artefact archivé et une tâche finale de nettoyage.

**Ce que je n'avais pas anticipé.** Que FakeNewsNet, la référence du domaine, ne
contienne aucune image — seulement des URL d'articles, dont beaucoup ne répondent plus.
La solution (lire la balise `og:image` de la page) fonctionne, mais avec un rendement
mesuré d'environ une image sur trois. C'est le genre d'écart entre la fiche d'un jeu de
données et sa réalité qu'on ne découvre qu'en le manipulant.

**Deux problèmes d'environnement instructifs.** Docker ne monte pas un dossier situé sur
un lecteur Google Drive : les montages sont créés vides, sans erreur, et le DAG n'est
jamais découvert. Et installer les dépendances au démarrage du conteneur remplaçait la
version de SQLAlchemy dont Airflow a besoin — d'où la construction d'une image sous
contrainte officielle.

**Ce sur quoi rester vigilant.** La concentration des sources : les flux RSS fournissent
la majorité du volume, et un jeu de données dominé par un seul émetteur transmet son
biais au modèle. C'est pour cela que la part de la source dominante est suivie comme un
KPI à part entière.

**Prochaine étape.** Déposer le jeu Fakeddit complet pour augmenter le volume labellisé,
et paralléliser l'extraction, aujourd'hui séquentielle source par source.
