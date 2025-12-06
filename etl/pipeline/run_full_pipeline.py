"""
Full ETL pipeline execution entrypoint.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

from etl.ingest.download_inmet import download_years
from etl.ingest.extract_zip import extract_year_zip, list_extracted_csvs
from etl.ingest.list_available_sources import expected_years
from etl.load.load_to_postgres import load_dataframe
from etl.load.validate_schema import validate_columns
from etl.transform.compute_heat_metrics import add_heat_metrics
from etl.transform.geospatial_enrichment import enrich_with_geospatial
from etl.transform.normalize_inmet import normalize_csv
from etl.utils.logger import get_logger
from etl.utils.timers import time_block

logger = get_logger(__name__)


def _process_csv(csv_path: Path) -> Optional[pd.DataFrame]:
    try:
        df = normalize_csv(csv_path)
        df = add_heat_metrics(df)
        df = enrich_with_geospatial(df)
        df = validate_columns(df)
        return df
    except Exception:
        logger.exception("Failed to process %s", csv_path)
        return None


def run_full(years: Optional[List[int]] = None) -> None:
    """Run full pipeline across all expected years."""
    year_list = years or expected_years()
    logger.info("Running full pipeline for years: %s", year_list)

    with time_block("full_pipeline"):
        archives = download_years(year_list)
        for zip_path in archives:
            try:
                extracted_dir = extract_year_zip(zip_path)
                for csv_path in list_extracted_csvs(extracted_dir):
                    df = _process_csv(csv_path)
                    if df is not None and not df.empty:
                        load_dataframe(df)
            except Exception:
                logger.exception("Error processing archive %s", zip_path)
                continue


if __name__ == "__main__":  # pragma: no cover
    run_full()
