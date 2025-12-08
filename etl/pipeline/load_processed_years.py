"""
Load processed INMET CSVs that have already been extracted to database.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

from etl.ingest.extract_zip import list_extracted_csvs
from etl.load.load_to_postgres import load_dataframe
from etl.load.populate_dim_estacao import populate_dim_estacao
from etl.load.validate_schema import validate_columns
from etl.transform.compute_heat_metrics import add_heat_metrics
from etl.transform.geospatial_enrichment import enrich_with_geospatial
from etl.transform.normalize_inmet import normalize_csv
from etl.utils.constants import DATA_DIR, PROCESSED_DIR
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


def load_processed_years(years: Optional[List[int]] = None) -> None:
    """
    Load already-processed INMET CSV files into bronze_clima_pe_horario.
    
    This function assumes CSV files have already been extracted to PROCESSED_DIR.
    Use this when running incremental ETL with pre-extracted data.
    """
    if not years:
        logger.warning("No years specified for loading")
        return
    
    logger.info("Loading processed INMET data for years: %s", years)
    
    with time_block("load_processed_years"):
        # Ensure dimension tables are populated
        logger.info("Populating dimension tables...")
        populate_dim_estacao()
        
        # Load CSVs from PROCESSED_DIR
        for year in years:
            year_dir = PROCESSED_DIR / str(year)
            if not year_dir.exists():
                logger.warning("Directory not found: %s", year_dir)
                continue
            
            logger.info("Processing CSVs from %s", year_dir)
            
            # Get all CSV files
            csv_files = list(year_dir.glob("*.CSV"))
            if not csv_files:
                logger.warning("No CSV files found in %s", year_dir)
                continue
            
            logger.info("Found %d CSV files in %s", len(csv_files), year_dir)
            
            # Process each CSV
            for csv_path in csv_files:
                df = _process_csv(csv_path)
                if df is not None and not df.empty:
                    logger.debug("Loading %d rows from %s", len(df), csv_path.name)
                    load_dataframe(df)
                else:
                    logger.debug("Skipping empty/invalid CSV: %s", csv_path.name)


if __name__ == "__main__":  # pragma: no cover
    # Example: python -m etl.pipeline.load_processed_years
    # This should be called via CLI with specific years
    pass
