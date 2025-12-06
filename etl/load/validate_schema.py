"""
Schema validation helpers prior to loading into the database.
"""
from __future__ import annotations

from typing import List

import pandas as pd

from etl.utils.constants import CANONICAL_COLUMNS
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def validate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure dataframe contains all canonical columns and in order."""
    missing: List[str] = [c for c in CANONICAL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for load: {missing}")
    ordered = df[CANONICAL_COLUMNS]
    logger.info("Validated schema with %s rows", len(ordered))
    return ordered


__all__ = ["validate_columns"]
