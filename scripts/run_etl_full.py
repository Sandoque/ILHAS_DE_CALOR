#!/usr/bin/env python3
"""Run the full ETL pipeline for Observatório Estadual de Ilhas de Calor – PE."""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import List

# Ensure project root is on sys.path when run from anywhere
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.ingest.list_available_sources import expected_years
from etl.pipeline.run_full_pipeline import run_full

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    years_env = os.getenv("ETL_YEARS")
    years: List[int] | None = None
    if years_env:
        try:
            years = [int(y.strip()) for y in years_env.split(",") if y.strip()]
        except ValueError:
            logger.warning("Invalid ETL_YEARS format; falling back to defaults")
    if years is None:
        years = expected_years()

    logger.info("Starting full ETL for years: %s", years)
    run_full(years)
    logger.info("Full ETL completed")


if __name__ == "__main__":
    main()
