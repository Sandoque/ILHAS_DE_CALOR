"""Filter MapBiomas data to municipalities present in INMET climate data."""
from __future__ import annotations

from typing import Set

import pandas as pd
from sqlalchemy import create_engine, text

from etl.utils.constants import DATABASE_URL
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def _fetch_inmet_municipios() -> Set[int]:
    """Fetch distinct municipality geocodes from bronze_clima_pe_horario via climate_hourly."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not configured")
    engine = create_engine(DATABASE_URL)
    
    # Try to fetch from bronze table first, fall back to legacy
    queries = [
        "SELECT DISTINCT m.codigo_ibge FROM public.bronze_clima_pe_horario b "
        "JOIN dim_estacao e ON b.id_estacao = e.id_estacao "
        "JOIN dim_cidade_pe m ON e.id_cidade = m.id_cidade "
        "WHERE m.codigo_ibge IS NOT NULL",
        
        "SELECT DISTINCT municipality_geocode FROM public.climate_hourly WHERE municipality_geocode IS NOT NULL",
    ]
    
    for query_str in queries:
        try:
            query = text(query_str)
            with engine.connect() as conn:
                result = conn.execute(query)
                geocodes = {int(row[0]) for row in result if row[0] is not None}
            if geocodes:
                logger.info("Loaded %s municipality geocodes from database", len(geocodes))
                return geocodes
        except Exception as e:
            logger.debug("Query failed (%s), trying next query", str(e))
            continue
    
    logger.warning("Could not fetch municipality geocodes; returning empty set")
    return set()


def filter_municipios(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows whose geocode is present in INMET climate data."""
    if "geocode" not in df.columns:
        logger.warning("Column 'geocode' not found; returning empty dataframe")
        return df.iloc[0:0]
    geocodes = _fetch_inmet_municipios()
    
    if not geocodes:
        logger.warning("No geocodes found; returning empty dataframe")
        return df.iloc[0:0]
    
    filtered = df[df["geocode"].astype(int).isin(geocodes)].copy()
    logger.info("Filtered municipios by INMET list: %s -> %s", len(df), len(filtered))
    return filtered


__all__ = ["filter_municipios"]
