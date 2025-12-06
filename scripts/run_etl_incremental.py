#!/usr/bin/env python3
"""Run the incremental ETL pipeline for a specific year or missing years."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is on sys.path when run from anywhere
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.pipeline.run_incremental import run_incremental

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run incremental ETL")
    parser.add_argument("--year", type=int, help="Year to process (optional)")
    args = parser.parse_args()

    target_year: Optional[int] = args.year
    env_year = os.getenv("ETL_YEAR")
    if target_year is None and env_year:
        try:
            target_year = int(env_year)
        except ValueError:
            logger.warning("Invalid ETL_YEAR env; processing missing years")

    logger.info("Starting incremental ETL%s", f" for {target_year}" if target_year else " for missing years")
    run_incremental(target_year)
    logger.info("Incremental ETL completed")


if __name__ == "__main__":
    main()
