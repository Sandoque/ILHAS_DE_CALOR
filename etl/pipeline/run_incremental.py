"""
Incremental ETL runner that only processes years not present in the database.
"""
from __future__ import annotations

from typing import List, Optional

from etl.ingest.list_available_sources import expected_years
from etl.load.load_to_postgres import existing_years
from etl.pipeline.load_processed_years import load_processed_years
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def missing_years(target_year: Optional[int] = None) -> List[int]:
    """Determine which years are not yet loaded into the database."""
    target = [target_year] if target_year else expected_years()
    loaded = existing_years()
    to_process = [year for year in target if year not in loaded]
    logger.info("Missing years to ingest: %s", to_process)
    return to_process


def run_incremental(target_year: Optional[int] = None) -> None:
    years = missing_years(target_year)
    if not years:
        logger.info("No missing years detected; nothing to do.")
        return
    load_processed_years(years)


if __name__ == "__main__":  # pragma: no cover
    run_incremental()
