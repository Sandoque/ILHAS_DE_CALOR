"""Filter MapBiomas data to municipalities present in INMET climate data."""
from __future__ import annotations

from typing import Set

import pandas as pd
from sqlalchemy import create_engine, text

from etl.utils.constants import DATABASE_URL
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def _fetch_inmet_municipios() -> Set[int]:
    """Fetch distinct municipality geocodes from climate_hourly."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not configured")
    engine = create_engine(DATABASE_URL)
    query = text(
        "SELECT DISTINCT municipality_geocode FROM public.climate_hourly WHERE municipality_geocode IS NOT NULL"
    )
    with engine.connect() as conn:
        result = conn.execute(query)
        geocodes = {int(row[0]) for row in result if row[0] is not None}
    logger.info("Loaded %s municipality geocodes from climate_hourly", len(geocodes))
    return geocodes


def filter_municipios(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows whose geocode is present in climate_hourly."""
    if "geocode" not in df.columns:
        logger.warning("Column 'geocode' not found; returning empty dataframe")
        return df.iloc[0:0]
    geocodes = _fetch_inmet_municipios()
    filtered = df[df["geocode"].astype(int).isin(geocodes)].copy()
    logger.info("Filtered municipios by INMET list: %s -> %s", len(df), len(filtered))
    return filtered


__all__ = ["filter_municipios"]
