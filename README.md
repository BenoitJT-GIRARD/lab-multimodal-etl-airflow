# CheckItAI — extraction de données multimodales pour la détection de fake news

Projet OpenClassrooms n°12 — *Extrayez des données multimodales de sites web*.

Mission : je suis ingénieur data junior chez **CheckItAI**, une start-up qui développe
des outils de détection automatique de désinformation. Mon objectif est de construire un
**pipeline ETL automatisé** qui récupère des publications **multimodales (texte + image)**
depuis plusieurs sources, les transforme en un jeu de données propre et structuré, puis les
charge dans une base adaptée — le tout orchestré par **Apache Airflow** et suivi par un
**tableau de bord KPI**.

## Structure

```
checkitai/
├── src/checkitai/          # package : sources, extraction, transformation, chargement, KPI
│   ├── config.py           # chemins et paramètres configurables (dataclasses)
│   ├── logging_setup.py    # journalisation centralisée
│   ├── schema.py           # schéma de la publication multimodale + validation
│   ├── sources/            # un module par source (RSS, NewsData.io, FakeNewsNet)
│   ├── extract.py          # étape E : collecte → JSON brut
│   ├── transform.py        # étape T : nettoyage, validation image, mapping → CSV/Parquet
│   ├── load.py             # étape L : chargement en base (SQLite / PostgreSQL)
│   └── kpi.py              # calcul des indicateurs de performance du pipeline
├── notebooks/              # déroulé pédagogique étape par étape (livrables 2, 3, 6)
├── scripts/                # points d'entrée reproductibles (CLI)
├── dags/                   # DAG Airflow (livrable 5)
├── docker/                 # docker-compose Airflow (exécution locale)
├── dashboard/              # application Streamlit (livrable 6)
├── docs/                   # rapport de sources, schéma, plan de monitoring, auto-évaluation
├── data/                   # raw / processed / samples / db (artefacts ignorés par git)
├── tests/                  # tests unitaires (pytest)
└── reports/                # livrables empaquetés pour OpenClassrooms
```

## Installation (uv)

```powershell
uv sync --extra dev          # crée .venv (Python 3.12) et installe tout
uv run pre-commit install    # active les hooks qualité
```

## Pipeline reproductible

Chaque étape est exécutable indépendamment, sans intervention manuelle :

```powershell
uv run python scripts/run_extraction.py        # 1. extraction → data/raw/*.json
uv run python scripts/run_transformation.py     # 2. transformation → data/processed/*.parquet
uv run python scripts/run_etl.py                # 3. ETL complet (extract + transform + load)
uv run streamlit run dashboard/app.py           # 4. tableau de bord KPI
```

Orchestration Airflow (Docker) — voir `docs/runbook_airflow.md` :

```powershell
docker compose -f docker/docker-compose.airflow.yaml up -d
# Interface : http://localhost:8080  (DAG : checkitai_etl)
```

## Qualité

```powershell
uv run ruff check .          # lint
uv run ruff format .         # formatage
uv run pytest                # tests unitaires + couverture
uv run bandit -c pyproject.toml -r src
```

## Livrables (convention OpenClassrooms)

Les sept livrables sont regroupés et empaquetés par `scripts/package_deliverables.py`
dans `reports/Girard_Benoit_12_<date>/` puis archivés en `.zip`.

| # | Livrable | Emplacement |
|---|----------|-------------|
| 1 | Rapport d'exploration de sources | `docs/rapport_exploration_sources.md` |
| 2 | Scripts d'extraction automatisée | `src/checkitai/sources/`, `notebooks/02_extraction.ipynb` |
| 3 | Pipeline de transformation reproductible | `src/checkitai/transform.py`, `notebooks/03_transformation.ipynb` |
| 4 | Schéma de données finalisé | `docs/schema_donnees.mmd` (+ rendu PNG/PDF) |
| 5 | Flux ETL Airflow | `dags/checkitai_etl_dag.py`, `docker/` |
| 6 | Tableau de bord KPI | `dashboard/app.py`, `notebooks/04_kpi.ipynb` |
| 7 | Plan de monitoring | `docs/plan_monitoring.md` |

## Contexte métier

Un détecteur de fake news multimodal a besoin d'un flux constant de publications fraîches,
labellisées et associant correctement **texte** et **image**. La qualité du dataset
conditionne directement la performance du modèle : ce pipeline garantit la fraîcheur,
la traçabilité et la reproductibilité des données ingérées.

## Licence

MIT
