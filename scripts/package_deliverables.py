"""Empaquette les livrables pour le dépôt OpenClassrooms.

Construit le dossier ``reports/Extrayez_donnees_multimodales_Girard_Benoit/`` avec
les livrables nommés selon la convention demandée — ``Nom_Prenom_n°_nom_date`` — puis
crée l'archive ZIP correspondante. Une copie complète du code source est jointe sous
``source/`` pour que le projet soit rejouable.

Usage :
    uv run python scripts/package_deliverables.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

# Convention OpenClassrooms : date de démarrage du projet au format mmaaaa.
DATE_TAG = "062026"
NOM_PRENOM = "Girard_Benoit"
TITRE_PROJET = "Extrayez_donnees_multimodales"

# (numéro de livrable, libellé, fichier source) — l'ordre suit la fiche livrables.
LIVRABLES: tuple[tuple[int, str, str], ...] = (
    (1, "rapport_exploration", "docs/rapport_exploration_sources.md"),
    (2, "extraction", "notebooks/02_extraction.ipynb"),
    (3, "transformation", "notebooks/03_transformation.ipynb"),
    (4, "schema_donnees", "docs/schema_donnees.pdf"),
    (5, "flux_etl_airflow", "dags/checkitai_etl_dag.py"),
    (6, "tableau_bord_kpi", "dashboard/app.py"),
    (7, "plan_monitoring", "docs/plan_monitoring.md"),
    (8, "presentation", "reports/presentation.pptx"),
    (9, "auto_evaluation", "docs/auto_evaluation.md"),
)

# Fichiers/dossiers annexes copiés sous source/ pour la reproductibilité.
SOURCE_ITEMS: tuple[str, ...] = (
    "src",
    "scripts",
    "dags",
    "dashboard",
    "notebooks",
    "docs",
    "tests",
    "docker",
    "data/samples",
    "README.md",
    "pyproject.toml",
    ".pre-commit-config.yaml",
    ".env.example",
    ".python-version",
    "LICENSE",
)


def _copie(src: Path, dst: Path) -> None:
    """Copie un fichier ou un dossier."""
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> None:
    """Construit le dossier de livrables puis l'archive ZIP."""
    dossier = REPORTS_DIR / f"{TITRE_PROJET}_{NOM_PRENOM}"
    if dossier.exists():
        shutil.rmtree(dossier)
    dossier.mkdir(parents=True, exist_ok=True)

    # 1. Livrables numérotés.
    manquants: list[str] = []
    for numero, libelle, chemin_relatif in LIVRABLES:
        source = ROOT / chemin_relatif
        if not source.exists():
            manquants.append(chemin_relatif)
            continue
        cible = dossier / f"{NOM_PRENOM}_{numero}_{libelle}_{DATE_TAG}{source.suffix}"
        _copie(source, cible)
        print(f"[ok] livrable {numero} : {cible.name}")

        # Annexes du schéma (mmd + png à côté du PDF).
        if libelle == "schema_donnees":
            for ext in (".mmd", ".png"):
                annexe = source.with_suffix(ext)
                if annexe.exists():
                    _copie(annexe, dossier / f"{NOM_PRENOM}_{numero}_{libelle}_{DATE_TAG}{ext}")

        # Annexes du flux ETL : les journaux d'exécution et les captures d'écran.
        if libelle == "flux_etl_airflow":
            preuve = ROOT / "docs" / "preuve_execution_airflow.md"
            if preuve.exists():
                _copie(preuve, dossier / f"{NOM_PRENOM}_{numero}_{libelle}_preuve_{DATE_TAG}.md")

            captures = ROOT / "reports" / "figures" / "airflow"
            if captures.exists():
                _copie(captures, dossier / f"{NOM_PRENOM}_{numero}_{libelle}_captures_{DATE_TAG}")

    if manquants:
        print(f"[warn] livrables introuvables (à générer d'abord) : {manquants}")

    # 2. Copie du code source pour reproductibilité.
    source_dir = dossier / "source"
    for item in SOURCE_ITEMS:
        chemin = ROOT / item
        if chemin.exists():
            _copie(chemin, source_dir / item)
    print(f"[ok] code source copié sous {source_dir.name}/")

    # 3. Archive ZIP.
    archive = shutil.make_archive(str(REPORTS_DIR / f"{TITRE_PROJET}_{NOM_PRENOM}"), "zip", dossier)
    print(f"[ok] archive créée : {Path(archive).name}")
    if manquants:
        sys.exit(1)


if __name__ == "__main__":
    main()
