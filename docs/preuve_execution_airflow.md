# Preuve d'exécution du DAG dans Apache Airflow

**Livrable n°5** — journaux d'exécution du DAG `checkitai_etl`.

Environnement : Apache Airflow 2.10.4, `LocalExecutor`, base de métadonnées PostgreSQL,
image construite depuis `docker/Dockerfile`. Procédure complète dans
`docs/runbook_airflow.md`.

---

## 1. Le DAG est chargé, sans erreur d'import

```
$ airflow dags list
dag_id        | fileloc                                | owners    | is_paused
==============+========================================+===========+==========
checkitai_etl | /opt/airflow/dags/checkitai_etl_dag.py | checkitai | None

$ airflow dags list-import-errors
No data found

$ airflow tasks list checkitai_etl --tree
<Task(PythonOperator): extraction>
    <Task(PythonOperator): transformation>
        <Task(PythonOperator): chargement>
            <Task(PythonOperator): metriques>
                <Task(PythonOperator): nettoyage>
```

Cinq tâches distinctes, une par étape du pipeline.

---

## 2. Exécution complète du DAG

```
$ airflow dags test checkitai_etl 2026-08-20
```

Extrait des journaux — les lignes de progression d'Airflow ont été conservées, les lignes
de débogage retirées.

```
[DAG TEST] starting task_id=extraction map_index=-1
checkitai.pipeline   | === ÉTAPE 1 — EXTRACTION ===
checkitai.extract    | Extraction : source 'rss' -> 97 publications
checkitai.extract    | Extraction : source 'newsdata' -> 10 publications
checkitai.opengraph  | Open Graph : 13 images retrouvées sur 40 articles consultés
checkitai.extract    | Extraction : source 'fakenewsnet' -> 48 publications
checkitai.extract    | Extraction : source 'kaggle_fakeddit' -> 24 publications
checkitai.extract    | Extraction : 179 publications brutes au total
checkitai.images     | Images : 116 téléchargées, 4 échecs, 59 ignorées (3.2 Mo sur disque)
checkitai.extract    | Extraction : 179 publications écrites dans data/raw/raw_publications_20260820_093505.json
checkitai.transit    | Transit : 'extraction.json' déposé pour l'étape suivante
Marking task as SUCCESS. task_id=extraction

[DAG TEST] starting task_id=transformation map_index=-1
checkitai.pipeline   | === ÉTAPE 2 — TRANSFORMATION ===
checkitai.transform  | Transformation : 179 publications brutes lues
checkitai.transform  | Transformation : 114/179 publications valides après nettoyage
checkitai.transform  | Transformation : 0 doublons retirés
checkitai.transform  | Transformation : dataset de 114 lignes exporté vers data/processed/publications_20260820_093506.parquet
checkitai.transit    | Transit : 'dataset.parquet' déposé pour l'étape suivante
Marking task as SUCCESS. task_id=transformation

[DAG TEST] starting task_id=chargement map_index=-1
checkitai.pipeline   | === ÉTAPE 3 — CHARGEMENT ===
checkitai.load       | Chargement : 114 lignes ajoutées dans 'publication'
checkitai.load       | Chargement : 6 lignes ajoutées dans 'source'
checkitai.load       | Chargement : 114 lignes ajoutées dans 'contenu_texte'
checkitai.load       | Chargement : 114 lignes ajoutées dans 'contenu_image'
checkitai.load       | Chargement : 18 lignes ajoutées dans 'label'
checkitai.load       | Chargement : 114 lignes ajoutées dans 'publications'
checkitai.load       | Chargement : 114 nouvelles publications, 0 déjà présentes
Marking task as SUCCESS. task_id=chargement

[DAG TEST] starting task_id=metriques map_index=-1
checkitai.pipeline   | === ÉTAPE 4 — MÉTRIQUES ===
checkitai.pipeline   | Métriques : fiche d'exécution écrite dans data/processed/runs/run_20260820_093506.json
Marking task as SUCCESS. task_id=metriques

[DAG TEST] starting task_id=nettoyage map_index=-1
checkitai.pipeline   | === ÉTAPE 5 — NETTOYAGE ===
checkitai.transit    | Transit : 5 fichiers temporaires supprimés
Marking task as SUCCESS. task_id=nettoyage

DagRun Finished: dag_id=checkitai_etl, run_id=manual__2026-08-20T00:00:00+00:00,
state=success, run_type=manual
```

Les cinq tâches sont en `SUCCESS` et le `DagRun` se termine en `state=success`. Les
quatre sources ont contribué, 116 images ont été téléchargées, et la zone de transit a
été vidée par la dernière tâche.

---

## 3. Une tâche rejouée seule

C'est le point qui justifie l'orchestration : chaque tâche doit pouvoir être relancée
indépendamment des autres. La zone de transit vient d'être vidée par la tâche
`nettoyage`, donc `transformation` n'a plus son fichier d'entrée.

```
$ airflow tasks test checkitai_etl transformation 2026-08-20
```

```
airflow.task         | Executing <Task(PythonOperator): transformation> on 2026-08-20
checkitai.pipeline   | === ÉTAPE 2 — TRANSFORMATION ===
checkitai.transit    | Transit : 'extraction.json' absent, reprise de l'archive raw_publications_20260820_093505.json
checkitai.transform  | Transformation : 179 publications brutes lues
checkitai.transform  | Transformation : 114/179 publications valides après nettoyage
checkitai.transform  | Transformation : dataset de 114 lignes exporté vers data/processed/publications_20260820_093518.parquet
checkitai.transit    | Transit : 'dataset.parquet' déposé pour l'étape suivante
Marking task as SUCCESS. task_id=transformation
```

La tâche a détecté l'absence du fichier de transit, est repartie de la dernière extraction
archivée, et s'est terminée en succès — **sans rejouer l'extraction**, qui prend une
trentaine de secondes et consomme un appel d'API.

---

## 4. Chargement incrémental

Une seconde exécution, lancée derrière celle-ci, ne recharge pas les mêmes données :

```
[ok] publications extraites  : 179
[ok] nouvelles en base       : 9
[ok] total accumulé en base  : 123
```

Sur 179 publications collectées, seules 9 étaient absentes de la base — les flux RSS
n'avaient publié que quelques articles entre les deux exécutions. Le jeu de données
s'enrichit au fil des exécutions quotidiennes, sans doublon et sans écraser l'historique.

---

## 5. Captures d'écran de l'interface

Les captures de la vue *Graph*, de la vue *Grid* et du log de la tâche `chargement` sont
à joindre depuis <http://localhost:8080> — voir le §5 du runbook.
