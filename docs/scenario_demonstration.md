# Scénario de démonstration — session de bilan

Déroulé de la démonstration du pipeline, dans l'ordre. Compter une quinzaine de minutes.

## Avant de commencer

```powershell
uv sync --extra dev
Copy-Item .env.example .env          # renseigner NEWSDATA_API_KEY si disponible
docker compose -f docker/docker-compose.airflow.yaml up -d
```

Rappel : Airflow doit être lancé depuis une copie du projet sur un **disque local**
(cf. §1 du runbook). Vérifier que <http://localhost:8080> répond avant de commencer.

---

## 1. Le problème à résoudre (1 min)

Un détecteur de fake news multimodal a besoin d'un flux continu de publications associant
**un texte et une image**. Sans automatisation, ce jeu de données vieillit et le modèle
se dégrade. Le pipeline collecte, nettoie et stocke ces publications tous les jours, sans
intervention.

Montrer le rapport d'exploration (`docs/rapport_exploration_sources.md`) : quatre sources
retenues, quatre méthodes d'accès différentes, et pourquoi le scraping a été écarté.

---

## 2. Une étape isolée (2 min)

```powershell
uv run python scripts/run_extraction.py
```

Ce qu'on regarde dans les logs pendant l'exécution :

- les quatre sources appelées l'une après l'autre, chacune isolée dans son `try/except` ;
- la ligne `Open Graph : N images retrouvées sur M articles consultés` — l'enrichissement
  multimodal des données FakeNewsNet, qui ne contiennent pas d'image ;
- la ligne `Images : N téléchargées, M échecs` — les fichiers réellement récupérés.

Puis ouvrir `data/raw/images/` : **les images sont sur le disque**, et le JSON brut
contient le texte et le chemin de son image.

---

## 3. Le pipeline complet (3 min)

```powershell
uv run python scripts/run_etl.py
```

Les cinq étapes s'enchaînent. Points à commenter :

- `Transformation : N/M publications valides` — les publications sans image sont
  écartées, c'est la règle du jeu de données ;
- `Chargement : N lignes ajoutées dans 'publication' / 'source' / 'contenu_texte'…` — le
  modèle conceptuel se retrouve tel quel en base, relié par ses clés de jointure ;
- `Chargement : N nouvelles publications, M déjà présentes` — le chargement est
  incrémental, le jeu de données grossit sans doublon ;
- `Transit : N fichiers temporaires supprimés` — la dernière étape fait le ménage.

Montrer la base :

```powershell
uv run python -c "import sqlite3; c=sqlite3.connect('data/db/checkitai.db'); print(c.execute('SELECT p.id, s.source, t.title FROM publication p JOIN source s ON s.source_id=p.source_id JOIN contenu_texte t ON t.id=p.id LIMIT 5').fetchall())"
```

---

## 4. L'orchestration Airflow (4 min)

Sur <http://localhost:8080>, déclencher `checkitai_etl` et ouvrir la vue **Graph** :
cinq tâches distinctes, `extraction → transformation → chargement → metriques →
nettoyage`.

**Le point à démontrer : les tâches sont indépendantes.** La zone de transit vient d'être
vidée par la tâche `nettoyage` ; on relance quand même la transformation seule :

```powershell
docker compose -f docker/docker-compose.airflow.yaml exec airflow-scheduler `
  airflow tasks test checkitai_etl transformation 2026-08-20
```

Le log affiche `Transit : 'extraction.json' absent, reprise de l'archive …` puis la tâche
se termine en succès. Aucune étape n'a besoin qu'une autre soit en mémoire : chacune
écrit son résultat sur disque, et retombe sur le dernier artefact archivé si le fichier
temporaire a disparu. C'est ce qui permet de rejouer une étape coûteuse sans rejouer
celles d'avant.

Ouvrir enfin le log de la tâche `chargement` dans l'interface.

---

## 5. Les KPI (4 min)

```powershell
uv run streamlit run dashboard/app.py
```

Parcourir dans l'ordre :

1. **État du pipeline** — chaque indicateur face à son seuil, en vert, orange ou rouge.
   Préciser que ces seuils ne sont pas recopiés du plan de monitoring : ils viennent du
   même dictionnaire dans le code, document et application ne peuvent pas diverger.
2. **Qualité** — taux de validité, association texte-image, publications datées.
3. **Volume, fraîcheur et coût** — total accumulé en base, âge médian des publications,
   disque occupé par les images.
4. **Performance** — durée par étape, débit, apport réel de l'exécution.
5. **Historique** — l'évolution d'une exécution à l'autre : c'est la tendance qui alerte,
   pas la valeur isolée.
6. **Ce que le pipeline produit** — les vignettes d'images, à côté de leurs titres. C'est
   la démonstration visuelle que chaque ligne du jeu de données est bien multimodale.

---

## 6. Qualité du code (1 min)

```powershell
uv run pytest -q
uv run ruff check .
uv run bandit -c pyproject.toml -r src
```

---

## Questions à préparer

**Pourquoi pas de scraping ?** Coût de maintenance permanent, conditions d'utilisation,
et les flux officiels exposent déjà la même donnée. Détaillé au §3 du rapport
d'exploration.

**Pourquoi passer par des fichiers plutôt que par XCom ?** XCom lie les tâches entre
elles : la transformation ne peut plus tourner sans que l'extraction ait tourné dans la
même exécution. Avec un fichier de transit, chaque tâche est autonome — et c'est
précisément ce qu'on attend d'un orchestrateur.

**Pourquoi une base relationnelle ?** Donnée tabulaire, schéma fixe, requêtes par filtres.
Le modèle éclaté prépare les jointures ; la table à plat sert l'entraînement.

**Que se passe-t-il si une source tombe ?** Elle est journalisée et comptée dans
`sources_en_echec` ; les autres continuent. Deux sources muettes le même jour déclenchent
une alerte rouge.

**Les données de Fakeddit sont-elles réelles ?** Le connecteur lit le jeu Kaggle réel
lorsqu'il est déposé dans `data/raw/kaggle/`. En son absence, il utilise un échantillon
de démonstration versionné, aux mêmes colonnes, avec des images libres de droits — pour
que le pipeline reste exécutable par n'importe qui. Les trois autres sources sont
réelles, dont les CSV FakeNewsNet téléchargés depuis GitHub.
