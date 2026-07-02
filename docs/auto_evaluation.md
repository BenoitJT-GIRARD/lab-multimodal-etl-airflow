# Fiche d'auto-évaluation — CheckItAI

**Projet n°12 — Extrayez des données multimodales de sites web**
**Auteur :** Benoit Girard

Toutes les cases sont cochées : chaque indicateur de réussite est satisfait et
documenté ci-dessous par l'artefact correspondant (colonne *Notes / preuve*).

## Compétence — Extraire des données issues de toutes sources confondues

### Livrable : Rapport d'exploration de sources

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon rapport est structuré avec des sections claires. | `docs/rapport_exploration_sources.md` (8 sections numérotées). |
| ☑ | J'ai utilisé le format attendu : Markdown ou PDF. | Markdown (export PDF possible). |
| ☑ | J'ai collecté des données d'au moins 3 sources différentes. | RSS (presse), NewsData.io, FakeNewsNet — 3 sources intégrées + 1 piste (Hugging Face). |
| ☑ | J'ai identifié et décrit des formats adaptés au traitement/stockage. | JSON (brut), Parquet (dataset), base relationnelle (chargement) — argumenté §5. |

### Livrable : Scripts d'extraction automatisée (.py / .ipynb)

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon script s'exécute sans intervention manuelle. | `scripts/run_extraction.py` ; `extract_all()` orchestre les 3 sources. |
| ☑ | Mon code est structuré en fonctions claires. | Un module par source dans `src/checkitai/sources/`, fonctions `fetch_*`. |
| ☑ | Mon script gère les erreurs et j'utilise des logs. | `try/except` par source + `logging` centralisé (`logging_setup.py`). |
| ☑ | Les données extraites sont cohérentes avec mon cas d'usage. | Texte + image par publication, vérifié dans `notebooks/02_extraction.ipynb`. |

## Compétence — Transformer des données afin de les adapter à leur utilisation finale

### Livrable : Pipeline de transformation reproductible (.py / .ipynb)

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon script fonctionne sans erreur à partir des données extraites. | `scripts/run_transformation.py`, `src/checkitai/transform.py`. |
| ☑ | Mon pipeline est divisé en étapes claires. | `lit_brut` → `traite` → `exporte` (lecture / traitement / export). |
| ☑ | J'ai inclus des logs pour tracer chaque transformation. | `logging` à chaque étape (validité, doublons, export). |
| ☑ | J'ai utilisé des paramètres configurables. | `TransformConfig` (seuil texte, image obligatoire, format de sortie). |

### Livrable : Schéma de données finalisé (PDF / Mermaid)

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon schéma est lisible : champs et types bien définis. | `docs/schema_donnees.mmd` (+ `.png` / `.pdf`), dictionnaire `docs/schema_donnees.md`. |
| ☑ | J'ai inclus texte, images, métadonnées utiles. | Entités CONTENU_TEXTE, CONTENU_IMAGE, SOURCE, LABEL + métadonnées. |
| ☑ | Mon schéma garantit le lien entre texte et image. | Relations `1—1` PUBLICATION↔CONTENU_TEXTE et PUBLICATION↔CONTENU_IMAGE + champ `has_image`. |

## Compétence — Charger des données afin de les stocker dans un emplacement adapté

### Livrable : Flux ETL (Airflow, .py)

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon DAG s'exécute sans erreur dans Airflow. | Exécuté dans Airflow 2.10.4 (`airflow dags test checkitai_etl`) : 4 tâches en SUCCESS, 142 lignes chargées. Preuve : `docs/preuve_execution_airflow.txt`. Interface via `docker/` (cf. `docs/runbook_airflow.md`). |
| ☑ | Mes tâches sont bien séparées. | 4 PythonOperator distincts : `extract` → `transform` → `load` → `metriques`. |

## Compétence — Définir des indicateurs de performance pertinents

### Livrable : Tableau de bord KPI de l'ETL (.py / .ipynb)

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Le tableau est lisible, interactif, visualisations étiquetées. | `dashboard/app.py` (Streamlit + Plotly), `notebooks/04_kpi.ipynb`. |
| ☑ | Les KPI mesurent les points critiques du pipeline. | Validité, association texte-image, durée/étape, débit, coût API. |
| ☑ | Le tableau est compréhensible même par des non-techniciens. | Cartes commentées (infobulles) + graphiques en français étiquetés. |

### Livrable : Plan de monitoring (Markdown / PDF)

| ☑ | Indicateur | Notes / preuve |
|:--:|---|---|
| ☑ | Mon plan est clair et bien structuré. | `docs/plan_monitoring.md` (9 sections). |
| ☑ | Il couvre seuils d'alerte, gestion des erreurs, rythmes de vérification. | Tables de seuils 🟢🟠🔴 §3, gestion d'erreurs §4, fréquences §5. |
| ☑ | Mon plan est cohérent avec le contexte professionnel. | Aligné sur le besoin CheckItAI : fraîcheur, fiabilité, sécurité de la base. |
