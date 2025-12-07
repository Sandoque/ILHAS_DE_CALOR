"""Normalize MapBiomas coverage data to tidy format."""
from __future__ import annotations

import pandas as pd

from etl.utils.logger import get_logger

logger = get_logger(__name__)

IMPORTANT_CLASSES_PREFIXES = [
    "Urban Infrastructure",
    "Forest",
    "Water",
    "Agriculture",
    "Pasture",
]

YEAR_START = 2010
YEAR_END = 2024


def _is_important(class_name: str) -> bool:
    return any(class_name.startswith(prefix) for prefix in IMPORTANT_CLASSES_PREFIXES)


def filter_classes(df: pd.DataFrame) -> pd.DataFrame:
    if "class" not in df.columns:
        logger.warning("Column 'class' not found; returning empty dataframe")
        return df.iloc[0:0]
    df = df[df["class"].astype(str).apply(_is_important)].copy()
    logger.info("Filtered classes to important list: %s rows", len(df))
    return df


def pivot_years(df: pd.DataFrame) -> pd.DataFrame:
    year_cols = [str(y) for y in range(YEAR_START, YEAR_END + 1) if str(y) in df.columns]
    if not year_cols:
        logger.warning("No year columns found in dataframe")
        return df.iloc[0:0]

    id_vars = [
        "geocode",
        "municipality",
        "state",
        "class",
        "class_level_0",
        "class_level_1",
        "class_level_2",
        "class_level_3",
        "class_level_4",
    ]
    for col in id_vars:
        if col not in df.columns:
            df[col] = None

    melted = df.melt(id_vars=id_vars, value_vars=year_cols, var_name="year", value_name="area")
    melted["year"] = melted["year"].astype(int)
    melted["area"] = pd.to_numeric(melted["area"], errors="coerce")
    melted = melted.dropna(subset=["area"])
    melted = melted[(melted["year"] >= YEAR_START) & (melted["year"] <= YEAR_END)]
    logger.info("Pivoted to tidy format: %s rows", len(melted))
    return melted


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = filter_classes(df)
    df = pivot_years(df)
    return df


__all__ = ["normalize", "filter_classes", "pivot_years", "IMPORTANT_CLASSES_PREFIXES"]
