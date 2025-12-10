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
    "data (yyyy-mm-dd)": "date",
    "datahora": "datehour",
    "data_hora": "datehour",
    "hora_utc": "hour_utc",
    "hora utc": "hour_utc",  # INMET format with space
    "hora (utc)": "hour_utc",
    "hora": "hour_utc",
    "hr_utc": "hour_utc",
    
    # Temperature (INMET long names)
    "temperatura do ar - bulbo seco, horaria (°c)": "temperature",
    "temperatura do ar - bulbo seco, horaria (c)": "temperature",
    "temperatura máxima na hora ant. (aut) (°c)": "temp_max_c",
    "temperatura máxima na hora ant. (aut) (c)": "temp_max_c",
    "temperatura mínima na hora ant. (aut) (°c)": "temp_min_c",
    "temperatura mínima na hora ant. (aut) (c)": "temp_min_c",
    "temperatura do ponto de orvalho (°c)": "dew_point",
    "temperatura do ponto de orvalho (c)": "dew_point",
    # Short forms
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
    
    # Humidity (INMET long names)
    "umidade relativa do ar, horaria (%)": "humidity",
    "umidade rel. max. na hora ant. (aut) (%)": "humidity_max",
    "umidade rel. min. na hora ant. (aut) (%)": "humidity_min",
    # Short forms
    "umid_ins": "humidity",
    "umid_relativa": "humidity",
    "umi_ins": "humidity",
    "umid_rel": "humidity",
    "umid_max": "humidity_max",
    "umid_min": "humidity_min",
    
    # Wind (INMET long names)
    "vento, velocidade horaria (m/s)": "wind_speed",
    "vento, rajada maxima (m/s)": "wind_gust",
    "vento, direção horaria (gr) (° (gr))": "wind_direction",
    "vento, direção horaria (gr) (gr)": "wind_direction",
    # Short forms
    "vel_vento": "wind_speed",
    "vel_vento_max": "wind_gust",
    "velvento": "wind_speed",
    "direcao_vento": "wind_direction",
    "direcao_vento_rajada_max": "wind_direction",
    
    # Radiation & precipitation (INMET long names)
    "radiacao global (kj/m²)": "radiation",
    "radiacao global (kj/m2)": "radiation",
    "precipitação total, horário (mm)": "precipitation",
    "precipitação total, horário (mm)": "precipitation",
    "pressao atmosferica ao nivel da estacao, horaria (mb)": "pressure",
    "pressão atmosferica ao nivel da estacao, horaria (mb)": "pressure",
    # Short forms
    "rad_glob": "radiation",
    "radiacao": "radiation",
    "precipitacao": "precipitation",
    "precip": "precipitation",
    "prec_total": "precipitation",
    "pressao": "pressure",
    "pressao_atm": "pressure",
    
    # Station info
    "codigo (wmo)": "station_code",
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

REQUIRED_BASE_COLUMNS: List[str] = REQUIRED_FIELDS.copy()

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


def _extract_station_metadata(csv_path: Path) -> dict:
    """
    Extract station metadata from first 8 rows of INMET CSV.
    
    Returns dict with: codigo (station code), uf, regiao, estacao, latitude, longitude, altitude
    """
    try:
        with open(csv_path, encoding='iso-8859-1') as f:
            metadata = {}
            for i, line in enumerate(f):
                if i >= 8:  # Only read first 8 lines
                    break
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip().lstrip(';')  # Remove leading semicolon from INMET format
                    metadata[key] = value
        
        return {
            'station_code': metadata.get('codigo (wmo)', metadata.get('codigo', '')).strip(),
            'uf': metadata.get('uf', '').strip().upper(),
            'region': metadata.get('regiao', '').strip().upper(),
            'station_name': metadata.get('estacao', '').strip(),
            'latitude': metadata.get('latitude', ''),
            'longitude': metadata.get('longitude', ''),
            'altitude': metadata.get('altitude', ''),
        }
    except Exception as e:
        logger.warning(f"Could not extract station metadata from {csv_path}: {e}")
        return {}


def _read_csv(csv_path: Path) -> pd.DataFrame:
    """Read CSV trying common delimiters and encodings."""
    # INMET CSVs use ISO-8859-1 (Latin-1) encoding
    # First 8 rows are metadata (REGIAO, UF, ESTACAO, CODIGO, LAT, LONG, ALT, FUNDACAO)
    # Data header is on row 8 (0-indexed)
    encodings = ["iso-8859-1", "utf-8", "cp1252"]
    delimiters = [";", ",", "\t"]
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                return pd.read_csv(
                    csv_path, 
                    sep=delimiter, 
                    encoding=encoding, 
                    header=8,  # Skip first 8 rows of metadata, use row 8 as header
                    low_memory=False
                )
            except Exception:
                continue
    
    # Last resort
    logger.error("Could not read %s with any encoding/delimiter combination", csv_path)
    raise ValueError(f"Unable to read CSV: {csv_path}")


def _parse_datetime(df: pd.DataFrame) -> pd.Series:
    """Extract or parse datetime from various column combinations."""
    if "datehour" in df.columns:
        return pd.to_datetime(df["datehour"], errors="coerce")
    
    if "date" in df.columns and "hour_utc" in df.columns:
        # Try format: "2024/01/01" + "0000 UTC" → "2024/01/01 0000"
        date_str = df["date"].astype(str)
        hour_str = df["hour_utc"].astype(str).str.replace(" UTC", "").str.replace("UTC", "").str.strip()
        
        # Handle DD/MM/YYYY format (INMET)
        if date_str.str.match(r"\d{4}/\d{1,2}/\d{1,2}").any():
            # INMET uses YYYY/MM/DD format
            combined = date_str + " " + hour_str
            return pd.to_datetime(combined, format="%Y/%m/%d %H%M", errors="coerce")
        
        # Handle DD/MM/YYYY format (some legacy files)
        if date_str.str.match(r"\d{1,2}/\d{1,2}/\d{4}").any():
            combined = date_str + " " + hour_str
            return pd.to_datetime(combined, format="%d/%m/%Y %H%M", errors="coerce")
        
        # Fallback to generic parsing
        combined = date_str + " " + hour_str
        return pd.to_datetime(combined, format="%Y-%m-%d %H:%M", errors="coerce")
    
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
    utc_dt = pd.to_datetime(utc_dt, errors="coerce")
    # Ensure datetime is timezone-naive or UTC
    if utc_dt.dt.tz is None:  # type: ignore[attr-defined]
        # If naive, localize to UTC first
        utc_dt = utc_dt.dt.tz_localize(UTC_TZ, ambiguous="NaT", nonexistent="NaT")  # type: ignore[attr-defined]
    else:
        utc_dt = utc_dt.dt.tz_convert(UTC_TZ)  # type: ignore[attr-defined]
    
    # Convert to PE timezone
    pe_dt = utc_dt.dt.tz_convert(PE_TZ)  # type: ignore[attr-defined]
    
    # Return both UTC and local (without tz info for local)
    return utc_dt, pe_dt.dt.tz_localize(None)  # type: ignore[attr-defined]


def normalize_csv(csv_path: Path) -> pd.DataFrame:
    """
    Normalize a raw INMET CSV to the bronze schema.
    
    Performs:
      1. Extract metadata from file header
      2. Column name normalization
      3. UF=PE filtering
      4. Datetime parsing and timezone conversion
      5. Date/time component extraction
      6. Numeric type conversion
      7. Data validation
    """
    # Extract metadata from first 8 rows
    station_metadata = _extract_station_metadata(csv_path)
    
    df = _read_csv(csv_path)
    original_cols = list(df.columns)
    
    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    logger.debug("Normalizing %s with columns %s", csv_path, original_cols)

    # Map columns to canonical names
    mapped_cols = {col: COLUMN_MAP.get(col, col) for col in df.columns}
    df = df.rename(columns=mapped_cols)

    # Replace common sentinel missing values
    df.replace({-9999: pd.NA, -9999.0: pd.NA, -99999: pd.NA, -99999.0: pd.NA}, inplace=True)

    # Filter Pernambuco - check both dataframe column and metadata
    if "uf" in df.columns:
        df = df[df["uf"].astype(str).str.upper() == "PE"].copy()
        df = df.drop(columns=["uf"])
    elif station_metadata.get('uf') != 'PE':
        # If UF column not in data, check metadata and filter out non-PE
        logger.info("Skipping %s (UF=%s from metadata)", csv_path.name, station_metadata.get('uf'))
        return pd.DataFrame()  # Return empty dataframe
    
    # Parse datetime
    datetime_utc = _parse_datetime(df)
    datetime_utc, datetime_local = _convert_to_pe_time(datetime_utc)
    
    df["datetime_utc"] = datetime_utc
    df["datetime_local"] = datetime_local
    
    # Add station_code from metadata or filename
    if "station_code" not in df.columns or df["station_code"].isna().all():
        station_code = station_metadata.get('station_code')
        if not station_code:
            # Fallback: extract from filename
            import re
            match = re.search(r"_([A-Z]\d{3})_", csv_path.name)
            if match:
                station_code = match.group(1)
        
        if station_code:
            df["station_code"] = station_code
            logger.debug("Extracted station_code '%s' from metadata/filename", station_code)
        else:
            logger.warning("Could not extract station_code from metadata or filename %s", csv_path.name)
    
    # Add geospatial data from metadata
    lat_val = station_metadata.get('latitude')
    if isinstance(lat_val, str) and lat_val:
        df["latitude"] = pd.to_numeric(lat_val, errors='coerce')
    lon_val = station_metadata.get('longitude')
    if isinstance(lon_val, str) and lon_val:
        df["longitude"] = pd.to_numeric(lon_val, errors='coerce')
    alt_val = station_metadata.get('altitude')
    if isinstance(alt_val, str) and alt_val:
        df["altitude"] = pd.to_numeric(alt_val, errors='coerce')
    
    # Extract date/time components
    df["ano"] = df["datetime_utc"].dt.year  # type: ignore[attr-defined]
    df["mes"] = df["datetime_utc"].dt.month  # type: ignore[attr-defined]
    df["dia"] = df["datetime_utc"].dt.day  # type: ignore[attr-defined]
    df["hora"] = df["datetime_utc"].dt.hour  # type: ignore[attr-defined]
    
    # Convert numeric columns
    for col in OPTIONAL_NUMERIC_FIELDS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            # Drop outliers that exceed DB precision (abs >= 1000 becomes NaN)
            df[col] = df[col].where(df[col].abs() < 1000)
            # Radiation should not be negative; coerce negatives to NaN
            if col == "radiation":
                df[col] = df[col].where(df[col] >= 0)
            # Precipitation should not be negative
            if col == "precipitation":
                df[col] = df[col].where(df[col] >= 0)

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
    
    # Rename 'temperature' to 'temp_ins_c' for downstream compatibility
    if 'temperature' in normalized.columns and 'temp_ins_c' not in normalized.columns:
        normalized = normalized.rename(columns={'temperature': 'temp_ins_c'})
    
    return normalized.reset_index(drop=True)


__all__ = ["normalize_csv", "REQUIRED_BASE_COLUMNS"]
