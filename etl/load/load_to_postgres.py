"""
Load dataframes into PostgreSQL using SQLAlchemy.

Loads normalized INMET climate data into bronze_clima_pe_horario table.
"""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from etl.utils.constants import DATABASE_URL
from etl.utils.logger import get_logger

logger = get_logger(__name__)

# Target for INMET climate data
BRONZE_TABLE = "bronze_clima_pe_horario"
BRONZE_SCHEMA = "public"

# Legacy targets (for backwards compatibility)
LEGACY_TABLE = "climate_hourly"
LEGACY_SCHEMA = "public"


def _get_engine(database_url: Optional[str] = None) -> Engine:
    url = database_url or DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is not set")
    return create_engine(url)


def _get_station_id_map(engine: Engine) -> dict[str, int]:
    """Fetch mapping of station_code -> id_estacao from dim_estacao."""
    try:
        query = text("SELECT codigo_estacao, id_estacao FROM dim_estacao WHERE uf = 'PE'")
        with engine.connect() as conn:
            result = conn.execute(query)
            mapping = {row[0]: row[1] for row in result}
            logger.info("Loaded %s stations from dim_estacao", len(mapping))
            return mapping
    except Exception:
        logger.exception("Could not fetch station mapping from dim_estacao")
        return {}


def _prepare_bronze_dataframe(df: pd.DataFrame, station_map: dict[str, int]) -> pd.DataFrame:
    """Map climate data to bronze_clima_pe_horario schema."""
    bronze_df = pd.DataFrame()
    
    # Map station codes to id_estacao
    bronze_df["id_estacao"] = df["station_code"].map(station_map)
    
    # Handle date/time fields
    bronze_df["data_hora_utc"] = df["datetime_utc"]
    bronze_df["data_hora_local"] = df.get("datetime_local", df["datetime_utc"])
    
    # Extract date components
    bronze_df["ano"] = df["datetime_utc"].dt.year
    bronze_df["mes"] = df["datetime_utc"].dt.month
    bronze_df["dia"] = df["datetime_utc"].dt.day
    bronze_df["hora"] = df["datetime_utc"].dt.hour
    
    # Climate measurements
    bronze_df["precipitacao_mm"] = df.get("precipitation")
    bronze_df["pressao_hpa"] = df.get("pressure")
    bronze_df["radiacao_kj_m2"] = df.get("radiation")
    
    # Temperature fields
    bronze_df["temp_ar_c"] = df.get("temperature")
    bronze_df["temp_ponto_orvalho_c"] = df.get("dew_point")
    bronze_df["temp_max_ant"] = df.get("temp_max_c")
    bronze_df["temp_min_ant"] = df.get("temp_min_c")
    
    # Humidity fields
    bronze_df["umid_rel_pct"] = df.get("humidity")
    bronze_df["umid_max_ant"] = df.get("humidity_max")
    bronze_df["umid_min_ant"] = df.get("humidity_min")
    
    # Wind fields
    bronze_df["vento_dir_graus"] = df.get("wind_direction")
    bronze_df["vento_rajada_ms"] = df.get("wind_gust")
    bronze_df["vento_vel_ms"] = df.get("wind_speed")
    
    # Metadata
    bronze_df["nome_arquivo_origem"] = df.get("source_file", "unknown")
    bronze_df["linha_arquivo"] = df.get("line_number")
    
    # Drop rows with missing id_estacao (unmatched stations)
    initial_count = len(bronze_df)
    bronze_df = bronze_df.dropna(subset=["id_estacao"])
    if len(bronze_df) < initial_count:
        logger.warning("Dropped %s rows due to unmatched stations", initial_count - len(bronze_df))
    
    # Ensure id_estacao is int
    bronze_df["id_estacao"] = bronze_df["id_estacao"].astype(int)
    
    return bronze_df


def load_dataframe(df: pd.DataFrame, engine: Optional[Engine] = None, chunksize: int = 5000) -> None:
    """
    Load normalized climate data into bronze_clima_pe_horario.
    
    Falls back to legacy climate_hourly table if bronze table does not exist.
    """
    eng = engine or _get_engine()
    
    try:
        # Try to load into bronze table (new schema)
        station_map = _get_station_id_map(eng)
        if station_map:
            try:
                bronze_df = _prepare_bronze_dataframe(df, station_map)
                if not bronze_df.empty:
                    logger.info(
                        "Loading %s rows into %s.%s (bronze)",
                        len(bronze_df),
                        BRONZE_SCHEMA,
                        BRONZE_TABLE,
                    )
                    bronze_df.to_sql(
                        BRONZE_TABLE,
                        eng,
                        schema=BRONZE_SCHEMA,
                        if_exists="append",
                        index=False,
                        method="multi",
                        chunksize=chunksize,
                    )
                    logger.info("Successfully loaded %s rows into bronze table", len(bronze_df))
                return
            except Exception:
                logger.exception("Failed to load into bronze table; falling back to legacy table")
        
        # Fall back to legacy climate_hourly table
        logger.info(
            "Loading %s rows into %s.%s (legacy fallback)",
            len(df),
            LEGACY_SCHEMA,
            LEGACY_TABLE,
        )
        df.to_sql(
            LEGACY_TABLE,
            eng,
            schema=LEGACY_SCHEMA,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=chunksize,
        )
    except Exception:
        logger.exception("Failed to load data into both bronze and legacy tables")
        raise


def existing_years(engine: Optional[Engine] = None) -> set[int]:
    """Return a set of years already present in the bronze climate table."""
    eng = engine or _get_engine()
    query = text(
        f"SELECT DISTINCT ano FROM {BRONZE_SCHEMA}.{BRONZE_TABLE} WHERE ano IS NOT NULL"
    )
    try:
        with eng.connect() as conn:
            result = conn.execute(query)
            years = {int(row[0]) for row in result if row[0] is not None}
            logger.info("Found %s years already loaded in bronze table", len(years))
            return years
    except Exception:
        logger.exception("Could not fetch existing years from database; trying legacy table")
        # Fall back to legacy table
        query = text(
            f"SELECT DISTINCT EXTRACT(YEAR FROM date) AS year FROM {LEGACY_SCHEMA}.{LEGACY_TABLE}"
        )
        try:
            with eng.connect() as conn:
                result = conn.execute(query)
                years = {int(row[0]) for row in result if row[0] is not None}
                logger.info("Found %s years already loaded in legacy table", len(years))
                return years
        except Exception:
            logger.exception("Could not fetch existing years from either table")
            return set()


__all__ = ["load_dataframe", "existing_years"]


def existing_years(engine: Optional[Engine] = None) -> set[int]:
    """Return a set of years already present in the target table."""
    eng = engine or _get_engine()
    query = text(
        f"SELECT DISTINCT EXTRACT(YEAR FROM date) AS year FROM {TARGET_SCHEMA}.{TARGET_TABLE}"
    )
    try:
        with eng.connect() as conn:
            result = conn.execute(query)
            years = {int(row[0]) for row in result if row[0] is not None}
            logger.info("Found %s years already loaded", len(years))
            return years
    except Exception:
        logger.exception("Could not fetch existing years from database")
        return set()


__all__ = ["load_dataframe", "existing_years"]
