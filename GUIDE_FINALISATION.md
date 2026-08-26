# Actions restantes avant le dépôt

Le projet est complet et fonctionnel : le pipeline tourne de bout en bout, le DAG
s'exécute dans Airflow, les sept livrables sont produits et l'archive de dépôt est
générée. Ce mémo liste ce qui reste — des actions qui dépendent d'un compte en ligne,
d'un navigateur ou d'un choix personnel, et qu'aucun script ne peut faire à ma place.

---

## 1. Captures d'écran de l'interface Airflow

Le livrable n°5 demande des preuves d'exécution. Les journaux sont déjà archivés dans
`docs/preuve_execution_airflow.md` ; il manque les copies d'écran.

Airflow doit être lancé depuis une copie du projet sur un **disque local** — Docker ne
monte pas un dossier Google Drive (détaillé au §1 du runbook).

```powershell
docker compose -f docker/docker-compose.airflow.yaml build
docker compose -f docker/docker-compose.airflow.yaml up -d
```

Sur <http://localhost:8080> (`airflow` / `airflow`), déclencher `checkitai_etl` puis
capturer la vue **Graph** (cinq tâches vertes), la vue **Grid** et le **log** de la tâche
`chargement`. Ranger les images dans `reports/figures/airflow/`.

---

## 2. Déposer le jeu Fakeddit complet *(optionnel)*

Le connecteur Kaggle lit un échantillon de démonstration tant que le jeu réel n'est pas
là. Pour passer sur les vraies données : télécharger un `.tsv` depuis
<https://www.kaggle.com/datasets/vanshikavmittal/fakeddit-dataset>, le déposer dans
`data/raw/kaggle/`, et relancer le pipeline. Le connecteur bascule tout seul.

---

## 3. Cibler un PostgreSQL managé *(optionnel)*

Par défaut, le chargement se fait dans SQLite (`data/db/checkitai.db`), ce qui suffit à la
démonstration. Pour une base managée :

```powershell
uv add psycopg2-binary
# puis dans .env :
# CHECKITAI_DB_URL=postgresql+psycopg2://USER:MOTDEPASSE@HOTE:5432/postgres
uv run python scripts/run_etl.py
```

---

## 4. Publier sur GitHub

```powershell
git log --graph --oneline   # vérifier l'historique
git status                  # doit être propre
git remote add origin https://github.com/<compte>/checkitai.git
git push -u origin main
```

`.env`, `data/` et `.venv/` sont exclus par `.gitignore` : aucune clé ni donnée
volumineuse n'est publiée.

---

## 5. Déposer les livrables sur OpenClassrooms

```powershell
uv run python scripts/package_deliverables.py
```

Déposer `reports/Extrayez_donnees_multimodales_Girard_Benoit.zip`. Vérifier au passage la
date de démarrage dans le nom des fichiers (`062026`), réglée par `DATE_TAG` dans le
script.

---

## 6. Préparer la session de bilan

Le déroulé complet de la démonstration, minute par minute, est dans
`docs/scenario_demonstration.md` — avec les questions probables et leurs réponses.
Le support de présentation est `reports/presentation.pptx`.

---

*Ce mémo n'a d'utilité qu'avant le dépôt ; il peut être supprimé ensuite.*
