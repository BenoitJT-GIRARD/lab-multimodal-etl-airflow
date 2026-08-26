# Actions restantes avant le dépôt

Le projet est complet : le pipeline tourne de bout en bout sur des données réelles, le
DAG s'exécute dans Airflow avec journaux et captures d'écran à l'appui, les sept
livrables sont produits et l'archive de dépôt est générée.

Ce mémo liste ce qui reste, et rien n'y est bloquant.

---

## 1. Re-télécharger le jeu Fakeddit sur une autre machine

Le pipeline tourne aujourd'hui sur les **données réelles** : le fichier
`multimodal_test_public.tsv` (15,6 Mo) est présent dans `data/raw/kaggle/`. Comme `data/`
est ignoré par git, il ne suit pas le dépôt. Sur une autre machine, le re-télécharger
(procédure au §4.4 du rapport d'exploration) et le déposer au même endroit.

Sans ce fichier, le pipeline continue de fonctionner : le connecteur bascule
automatiquement sur l'échantillon de démonstration versionné.

---

## 2. Refaire des captures Airflow *(seulement si besoin)*

Les captures du livrable n°5 sont déjà dans `reports/figures/airflow/`. Pour les refaire :

Airflow doit être lancé depuis une copie du projet sur un **disque local** — Docker ne
monte pas un dossier Google Drive (détaillé au §1 du runbook).

```powershell
docker compose -f docker/docker-compose.airflow.yaml build
docker compose -f docker/docker-compose.airflow.yaml up -d
```

Sur <http://localhost:8080> (`airflow` / `airflow`), activer puis déclencher
`checkitai_etl`, et capturer la vue **Graph**, la vue **Grid** et le **log** de la tâche
`chargement`.

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
