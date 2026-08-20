"""Pipeline ETL complet, executable en une commande.

Enchaine les trois etapes — Extract, Transform, Load — en mesurant la duree de
chacune et en enregistrant les metriques d'execution (pour le tableau de bord
KPI et le monitoring). C'est la version « script » de reference ; le DAG Airflow
(livrable 5) reutilise exactement les memes fonctions, decoupees en taches.

Usage :
    uv run python scripts/run_etl.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from checkitai.config import (
    ExtractionConfig,
    LoadConfig,
    TransformConfig,
    ensure_dirs,
)
from checkitai.extract import extract_all, save_raw
from checkitai.kpi import RUNS_DIR
from checkitai.load import run_load
from checkitai.logging_setup import get_logger, setup_logging
from checkitai.sources import newsdata
from checkitai.transform import run_transformation

logger = get_logger("checkitai.etl")


def main() -> None:
    """Execute l'ETL de bout en bout et persiste les metriques."""
    setup_logging()
    ensure_dirs()
    durations: dict[str, float] = {}

    # --- Extract ---
    logger.info("=== ETAPE 1/3 : EXTRACTION ===")
    debut = time.perf_counter()
    records = extract_all(ExtractionConfig())
    raw_path = save_raw(records)
    durations["extract"] = time.perf_counter() - debut

    # --- Transform ---
    logger.info("=== ETAPE 2/3 : TRANSFORMATION ===")
    debut = time.perf_counter()
    dataset_path, stats = run_transformation(raw_path, TransformConfig())
    durations["transform"] = time.perf_counter() - debut

    # --- Load ---
    logger.info("=== ETAPE 3/3 : CHARGEMENT ===")
    debut = time.perf_counter()
    bilan_chargement = run_load(dataset_path, LoadConfig())
    rows_loaded = bilan_chargement["publications"]
    durations["load"] = time.perf_counter() - debut

    # --- Metriques d'execution ---
    run = {
        "run_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "durations_sec": durations,
        "rows_extracted": len(records),
        "rows_loaded": rows_loaded,
        "api_calls": 1 if newsdata.is_enabled() else 0,
        "stats": stats,
        "dataset_path": str(dataset_path),
    }
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_file = RUNS_DIR / f"run_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
    with run_file.open("w", encoding="utf-8") as handle:
        json.dump(run, handle, ensure_ascii=False, indent=2)

    logger.info("ETL termine : %d lignes chargees en %.2fs", rows_loaded, sum(durations.values()))
    print(f"[ok] ETL termine : {rows_loaded} publications chargees")
    print(f"[ok] metriques : {run_file}")


if __name__ == "__main__":
    main()
