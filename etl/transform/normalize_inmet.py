"""
Normalize raw INMET CSV files to bronze_clima_pe_horario schema filtered to Pernambuco (UF=PE).

Transforms INMET data into the canonical schema for loading into bronze_clima_pe_horario:
  - Standardizes column names
  - Converts timestamps to UTC and local Pernambuco time (UTC-3)
  - Extracts date/time components
  - Filters for Pernambuco only (UF=PE)
  - Validates required fields
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd
import pytz

from etl.utils.logger import get_logger

logger = get_logger(__name__)

# Timezone for Pernambuco
PE_TZ = pytz.timezone("America/Recife")
UTC_TZ = pytz.UTC

COLUMN_MAP: Dict[str, str] = {
    # Date/time
    "data": "date",
    "data_medicao": "date",
    "date": "date",
    "datahora": "datehour",
    "data_hora": "datehour",
    "hora_utc": "hour_utc",
    "hora": "hour_utc",
    "hr_utc": "hour_utc",
    
    # Temperature
    "temp_inst": "temperature",
    "temperatura": "temperature",
    "tem_ins": "temperature",
    "temp_ins_c": "temperature",
    "tempmax": "temp_max_c",
    "temp_max": "temp_max_c",
    "tem_max": "temp_max_c",
    "tempmin": "temp_min_c",
    "temp_min": "temp_min_c",
    "tem_min": "temp_min_c",
    "ponto_orvalho": "dew_point",
    "temp_ponto_orvalho": "dew_point",
    
    # Humidity
    "umid_ins": "humidity",
    "umid_relativa": "humidity",
    "umi_ins": "humidity",
    "umid_rel": "humidity",
    "umid_max": "humidity_max",
    "umid_min": "humidity_min",
    
    # Wind
    "vel_vento": "wind_speed",
    "vel_vento_max": "wind_gust",
    "velvento": "wind_speed",
    "direcao_vento": "wind_direction",
    "direcao_vento_rajada_max": "wind_direction",
    
    # Radiation & precipitation
    "rad_glob": "radiation",
    "radiacao": "radiation",
    "precipitacao": "precipitation",
    "precip": "precipitation",
    "prec_total": "precipitation",
    "pressao": "pressure",
    "pressao_atm": "pressure",
    
    # Station info
    "codigo_estacao": "station_code",
    "cd_estacao": "station_code",
    "estacao": "station_code",
    "latitude": "latitude",
    "vl_latitude": "latitude",
    "longitude": "longitude",
    "vl_longitude": "longitude",
    "altitude": "altitude",
    "vl_altitude": "altitude",
    "uf": "uf",
    "sigla_uf": "uf",
}

REQUIRED_FIELDS: List[str] = [
    "datetime_utc",
    "station_code",
]

OPTIONAL_NUMERIC_FIELDS: List[str] = [
    "temperature",
    "temp_max_c",
    "temp_min_c",
    "humidity",
    "wind_speed",
    "radiation",
    "precipitation",
    "latitude",
    "longitude",
    "altitude",
    "dew_point",
    "wind_gust",
    "wind_direction",
    "humidity_max",
    "humidity_min",
    "pressure",
]


def _read_csv(csv_path: Path) -> pd.DataFrame:
    """Read CSV trying common delimiters."""
    try:
        return pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)
    except Exception:
        logger.debug("Retrying %s with comma separator", csv_path)
        try:
            return pd.read_csv(csv_path, sep=",", encoding="utf-8", low_memory=False)
        except Exception:
            logger.debug("Retrying %s with tab separator", csv_path)
            return pd.read_csv(csv_path, sep="\t", encoding="utf-8", low_memory=False)


def _parse_datetime(df: pd.DataFrame) -> pd.Series:
    """Extract or parse datetime from various column combinations."""
    if "datehour" in df.columns:
        return pd.to_datetime(df["datehour"], errors="coerce")
    
    if "date" in df.columns and "hour_utc" in df.columns:
        return pd.to_datetime(
            df["date"].astype(str) + " " + df["hour_utc"].astype(str),
            format="%Y-%m-%d %H:%M",
            errors="coerce",
        )
    
    if "date" in df.columns:
        return pd.to_datetime(df["date"], errors="coerce")
    
    logger.warning("Could not determine datetime from available columns")
    return pd.Series([pd.NaT] * len(df))


def _convert_to_pe_time(utc_dt: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    Convert UTC datetime to Pernambuco local time (UTC-3).
    
    Returns:
        (datetime_utc, datetime_local)
    """
    # Ensure datetime is timezone-naive or UTC
    if utc_dt.dt.tz is None:
        utc_dt = utc_dt.astype("datetime64[ns, UTC]")
    else:
        utc_dt = utc_dt.dt.tz_convert(UTC_TZ)
    
    # Convert to PE timezone
    pe_dt = utc_dt.dt.tz_convert(PE_TZ)
    
    # Return both UTC and local (without tz info for local)
    return utc_dt, pe_dt.dt.tz_localize(None)


def normalize_csv(csv_path: Path) -> pd.DataFrame:
    """
    Normalize a raw INMET CSV to the bronze schema.
    
    Performs:
      1. Column name normalization
      2. UF=PE filtering
      3. Datetime parsing and timezone conversion
      4. Date/time component extraction
      5. Numeric type conversion
      6. Data validation
    """
    df = _read_csv(csv_path)
    original_cols = list(df.columns)
    
    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    logger.debug("Normalizing %s with columns %s", csv_path, original_cols)

    # Map columns to canonical names
    mapped_cols = {col: COLUMN_MAP.get(col, col) for col in df.columns}
    df = df.rename(columns=mapped_cols)

    # Filter Pernambuco
    if "uf" in df.columns:
        df = df[df["uf"].astype(str).str.upper() == "PE"].copy()
        df = df.drop(columns=["uf"])
    else:
        logger.warning("Column 'UF' not found in %s; keeping all rows", csv_path)

    # Parse datetime
    datetime_utc = _parse_datetime(df)
    datetime_utc, datetime_local = _convert_to_pe_time(datetime_utc)
    
    df["datetime_utc"] = datetime_utc
    df["datetime_local"] = datetime_local
    
    # Extract date/time components
    df["ano"] = df["datetime_utc"].dt.year
    df["mes"] = df["datetime_utc"].dt.month
    df["dia"] = df["datetime_utc"].dt.day
    df["hora"] = df["datetime_utc"].dt.hour
    
    # Convert numeric columns
    for col in OPTIONAL_NUMERIC_FIELDS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Add source metadata
    df["source_file"] = str(csv_path.name)
    df["line_number"] = df.index + 2  # +2 for header + 0-based indexing

    # Ensure required fields exist
    for col in REQUIRED_FIELDS:
        if col not in df.columns:
            df[col] = pd.NaT if col == "datetime_utc" else None

    # Filter out rows with missing critical data
    normalized = df.dropna(subset=["datetime_utc", "station_code"])
    
    logger.info(
        "Normalized %s rows from %s (dropped %s with missing critical fields)",
        len(normalized),
        csv_path,
        len(df) - len(normalized),
    )
    
    return normalized.reset_index(drop=True)


__all__ = ["normalize_csv", "REQUIRED_BASE_COLUMNS"]
