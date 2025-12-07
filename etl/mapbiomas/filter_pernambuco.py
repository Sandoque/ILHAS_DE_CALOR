"""Filter MapBiomas data for Pernambuco only."""
from __future__ import annotations

import pandas as pd

from etl.utils.logger import get_logger

logger = get_logger(__name__)


def filter_state(df: pd.DataFrame) -> pd.DataFrame:
    """Return only rows where state == Pernambuco."""
    if "state" not in df.columns:
        logger.warning("Column 'state' not found; returning empty dataframe")
        return df.iloc[0:0]
    filtered = df[df["state"].astype(str).str.strip().str.lower() == "pernambuco"].copy()
    logger.info("Filtered Pernambuco rows: %s -> %s", len(df), len(filtered))
    return filtered


__all__ = ["filter_state"]
