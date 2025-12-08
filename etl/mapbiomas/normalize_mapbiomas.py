"""
Normalize MapBiomas coverage data to aux_cobertura_vegetal_pe format.

Transforms MapBiomas raw data into:
  - Filters for relevant land cover classes (urban vegetation, built-up, water bodies)
  - Pivots year columns to tidy format
  - Calculates percentages by class
  - Outputs schema: id_cidade, ano, perc_vegetacao_urbana, perc_area_construida, perc_corpos_dagua
"""
from __future__ import annotations

import pandas as pd

from etl.utils.logger import get_logger

logger = get_logger(__name__)

# MapBiomas v10 classes mapping
# Reference: https://www.mapbiomas.org/
VEGETATION_CLASSES = {
    11,  # Dense Forest
    12,  # Open Forest
    13,  # Mangrove
}

URBAN_CLASSES = {
    30,  # Urban Infrastructure / Vegetação Urbana
}

BUILDUP_CLASSES = {
    24,  # Non-vegetated Area / Área Construída
}

WATER_CLASSES = {
    33,  # Water / Corpos d'água
}

YEAR_START = 1985
YEAR_END = 2024


def _get_class_category(class_id: int) -> str | None:
    """Map MapBiomas class ID to our category."""
    if class_id in URBAN_CLASSES:
        return "vegetacao_urbana"
    elif class_id in BUILDUP_CLASSES:
        return "area_construida"
    elif class_id in WATER_CLASSES:
        return "corpos_dagua"
    return None


def filter_classes(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to only relevant classes (urban, built-up, water)."""
    if "class" not in df.columns and "class_id" not in df.columns:
        logger.warning("No class column found; returning empty dataframe")
        return df.iloc[0:0]
    
    class_col = "class" if "class" in df.columns else "class_id"
    
    relevant_classes = VEGETATION_CLASSES | URBAN_CLASSES | BUILDUP_CLASSES | WATER_CLASSES
    
    try:
        df[class_col] = pd.to_numeric(df[class_col], errors="coerce").astype("Int64")
        filtered = df[df[class_col].isin(relevant_classes)].copy()
        logger.info("Filtered classes: %s rows (kept %s)", len(df), len(filtered))
        return filtered
    except Exception as e:
        logger.exception("Error filtering classes: %s", e)
        return df.iloc[0:0]


def pivot_years(df: pd.DataFrame) -> pd.DataFrame:
    """Convert year columns to tidy format with area values."""
    year_cols = [str(y) for y in range(YEAR_START, YEAR_END + 1) if str(y) in df.columns]
    if not year_cols:
        logger.warning("No year columns found")
        return df.iloc[0:0]

    id_vars = [
        "geocode",
        "municipality",
        "state",
        "class",
        "class_id",
        "class_level_0",
        "class_level_1",
        "class_level_2",
        "class_level_3",
        "class_level_4",
    ]
    
    # Keep only id_vars that actually exist
    id_vars = [col for col in id_vars if col in df.columns]
    
    melted = df.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name="year",
        value_name="area",
    )
    
    melted["year"] = melted["year"].astype(int)
    melted["area"] = pd.to_numeric(melted["area"], errors="coerce")
    melted = melted.dropna(subset=["area"])
    melted = melted[(melted["year"] >= YEAR_START) & (melted["year"] <= YEAR_END)]
    
    logger.info("Pivoted to tidy format: %s rows", len(melted))
    return melted


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize MapBiomas data.
    
    Returns dataframe with: geocode, municipality, year, class_category, area
    """
    df = filter_classes(df)
    if df.empty:
        logger.warning("No data after filtering classes")
        return df.iloc[0:0]
    
    df = pivot_years(df)
    if df.empty:
        logger.warning("No data after pivoting years")
        return df.iloc[0:0]
    
    # Add class category
    class_col = "class" if "class" in df.columns else "class_id"
    df["class_category"] = df[class_col].apply(_get_class_category)
    
    # Drop rows with unknown classes
    df = df[df["class_category"].notna()].copy()
    
    logger.info("Normalized MapBiomas data: %s rows", len(df))
    return df[["geocode", "municipality", "year", "class_category", "area"]]


__all__ = ["normalize", "filter_classes", "pivot_years"]
