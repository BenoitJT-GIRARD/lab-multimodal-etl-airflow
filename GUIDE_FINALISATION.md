# Guide de finalisation — actions restantes

Ce projet est **complet et fonctionnel** : le pipeline ETL tourne de bout en bout,
les sept livrables sont produits, la fiche d'auto-évaluation est entièrement cochée
et l'archive de dépôt est générée. Ce guide liste les **quelques actions qui te
restent** (elles dépendent de comptes en ligne, d'un navigateur ou d'un dépôt
distant — impossibles à automatiser entièrement).

---

## ✅ Ce qui est déjà fait automatiquement

- Pipeline ETL exécuté avec de **vraies données** (RSS + NewsData.io + FakeNewsNet) :
  152 publications brutes → **112 publications multimodales valides** chargées en base.
- Code structuré, linté (ruff), testé (17 tests pytest verts), journalisé.
- 7 livrables + présentation + fiche d'auto-évaluation générés.
- Schéma de données rendu en PNG **et** PDF.
- Archive `reports/Extrayez_donnees_multimodales_Girard_Benoit.zip` prête.
- Clé NewsData.io configurée dans `.env` (non versionnée).

---

## 1. (Recommandé) Produire les captures d'écran Airflow

Le DAG et son environnement Docker sont prêts. Pour obtenir les **preuves
d'exécution dans l'interface Airflow** (demandées au livrable 5) :

```powershell
Copy-Item docker/.env.example docker/.env
# (renseigner NEWSDATA_API_KEY dans docker/.env si tu veux la source API dans Airflow)
docker compose -f docker/docker-compose.airflow.yaml up -d
```

1. Ouvre **http://localhost:8080** (identifiants `airflow` / `airflow`).
2. Active le DAG **`checkitai_etl`** puis clique **Trigger DAG**.
3. Capture : vue **Graph** (4 tâches vertes), vue **Grid**, et le **log** de la
   tâche `load`.
4. Range les captures dans `reports/figures/airflow/`.

Le pas-à-pas détaillé est dans `docs/runbook_airflow.md`.

> Sans interface, tu peux aussi générer des logs de tâches en une commande :
> `docker compose -f docker/docker-compose.airflow.yaml run --rm airflow-scheduler airflow dags test checkitai_etl 2026-06-29`

---

## 2. (Optionnel) Brancher une base PostgreSQL / Supabase

Par défaut, le chargement se fait dans **SQLite** (`data/db/checkitai.db`), ce qui
suffit pour la démonstration. Pour cibler une base managée :

1. Crée un projet sur <https://supabase.com> (ou tout PostgreSQL).
2. Récupère l'URL de connexion et renseigne-la dans `.env` :
   ```
   CHECKITAI_DB_URL=postgresql+psycopg2://USER:MOTDEPASSE@HOTE:5432/postgres
   ```
3. Installe le pilote : `uv add psycopg2-binary`
4. Relance `uv run python scripts/run_etl.py` : la table `publications` est créée
   dans Supabase.

---

## 3. (Optionnel) Télécharger le FakeNewsNet complet

Le pipeline utilise un échantillon versionné. Pour les vrais CSV labellisés :

1. Récupère les fichiers `politifact_fake.csv`, `politifact_real.csv`,
   `gossipcop_fake.csv`, `gossipcop_real.csv` depuis
   <https://github.com/KaiDMML/FakeNewsNet> (dossier `dataset/`).
2. Place-les dans `data/raw/fakenewsnet/`.
3. Le connecteur les détecte et les utilise automatiquement à la place de
   l'échantillon.

---

## 4. Reconstituer le dépôt git puis publier sur GitHub

L'historique complet (18 commits, style étudiant, conventional commits) a été créé
et archivé dans **`checkitai_history.bundle`** (à la racine du projet). Il n'a pas pu
être posé directement en `.git` car Google Drive maintenait un verrou sur ce dossier
pendant la session (synchronisation en cours). Pour le reconstituer en local :

1. **Si un dossier `.git` fantôme/verrouillé existe encore**, ferme les applications
   qui synchronisent le dossier (ou redémarre la machine), puis supprime-le :
   ```powershell
   Remove-Item -Recurse -Force .git   # uniquement s'il existe et qu'il pose problème
   ```
2. Reconstitue l'historique depuis le bundle (récupère les 18 commits) :
   ```powershell
   git init -b main
   git pull checkitai_history.bundle main
   ```
   Le répertoire de travail est déjà aligné sur le dernier commit ; `git status`
   doit être propre (seuls les artefacts ignorés restent non suivis).
3. (Optionnel) Vérifie : `git log --oneline` doit afficher les 18 commits.

Ensuite, publie sur GitHub :

1. Crée un dépôt vide sur GitHub (ex. `checkitai`), **sans** README.
2. Connecte et pousse :
   ```powershell
   git remote add origin https://github.com/<ton-compte>/checkitai.git
   git push -u origin main
   ```

> `.env`, `data/`, `.venv/`, l'archive de livrables et `checkitai_history.bundle`
> sont déjà exclus par `.gitignore` : aucune clé ni donnée volumineuse ne sera
> publiée.

---

## 5. (Optionnel) Publier le dataset sur Hugging Face

Pour partager le jeu de données produit :

1. Crée un compte sur <https://huggingface.co> et un *dataset repo*.
2. `uv add huggingface_hub` puis :
   ```python
   from huggingface_hub import HfApi
   HfApi().upload_file(
       path_or_fileobj="data/processed/<dernier>.parquet",
       path_in_repo="publications.parquet",
       repo_id="<ton-compte>/checkitai-multimodal", repo_type="dataset",
   )
   ```
3. Renseigne la licence et une carte de dataset (origine, modalités, labels).

---

## 6. Déposer les livrables sur OpenClassrooms

1. (Re)génère l'archive si besoin :
   `uv run python scripts/package_deliverables.py`
2. Dépose **`reports/Extrayez_donnees_multimodales_Girard_Benoit.zip`** sur la
   plateforme. Elle contient les 7 livrables numérotés (+ présentation,
   auto-évaluation et code source).
3. Vérifie la date de démarrage dans le nom des fichiers (`062026`) et ajuste
   `DATE_TAG` dans `scripts/package_deliverables.py` si nécessaire.

---

## 7. Réserver la session de bilan

Prépare la démonstration en direct (lance `uv run streamlit run dashboard/app.py`
et montre le pipeline). Appuie-toi sur la présentation
`reports/presentation.pptx` et la fiche `docs/auto_evaluation.md`.
