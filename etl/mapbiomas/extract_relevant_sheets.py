"""Extract relevant sheets from MapBiomas XLSX."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from etl.utils.logger import get_logger

logger = get_logger(__name__)

RELEVANT_SHEET = "COVERAGE_10"


def load_sheet(xlsx_path: Path) -> pd.DataFrame:
    """Load the COVERAGE_10 sheet using pandas with openpyxl engine."""
    logger.info("Loading sheet %s from %s", RELEVANT_SHEET, xlsx_path)
    return pd.read_excel(xlsx_path, sheet_name=RELEVANT_SHEET, engine="openpyxl")


__all__ = ["load_sheet", "RELEVANT_SHEET"]
