"""
Normalize raw INMET CSV files to canonical schema filtered to Pernambuco (UF=PE).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pandas as pd

from etl.utils.logger import get_logger

logger = get_logger(__name__)


COLUMN_MAP: Dict[str, str] = {
    "data": "date",
    "data_medicao": "date",
    "date": "date",
    "datahora": "datehour",
    "data_hora": "datehour",
    "hora_utc": "hour_utc",
    "hora": "hour_utc",
    "hr_utc": "hour_utc",
    "temp_inst": "temp_ins_c",
    "temperatura": "temp_ins_c",
    "tem_ins": "temp_ins_c",
    "tempmax": "temp_max_c",
    "temp_max": "temp_max_c",
    "tem_max": "temp_max_c",
    "tempmin": "temp_min_c",
    "temp_min": "temp_min_c",
    "tem_min": "temp_min_c",
    "umid_ins": "humidity",
    "umid_relativa": "humidity",
    "umi_ins": "humidity",
    "vel_vento": "wind_speed",
    "vel_vento_max": "wind_speed",
    "velvento": "wind_speed",
    "rad_glob": "radiation",
    "radiacao": "radiation",
    "precipitacao": "precipitation",
    "precip": "precipitation",
    "prec_total": "precipitation",
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

REQUIRED_BASE_COLUMNS: List[str] = [
    "date",
    "hour_utc",
    "temp_ins_c",
    "temp_max_c",
    "temp_min_c",
    "humidity",
    "wind_speed",
    "radiation",
    "precipitation",
    "station_code",
    "latitude",
    "longitude",
    "altitude",
]


def _read_csv(csv_path: Path) -> pd.DataFrame:
    """Read CSV trying common delimiters."""
    try:
        return pd.read_csv(csv_path, sep=";", encoding="utf-8", low_memory=False)
    except Exception:
        logger.debug("Retrying %s with comma separator", csv_path)
        return pd.read_csv(csv_path, sep=",", encoding="utf-8", low_memory=False)


def normalize_csv(csv_path: Path) -> pd.DataFrame:
    """Normalize a raw CSV to the canonical schema for Pernambuco only."""
    df = _read_csv(csv_path)
    original_cols = list(df.columns)
    df.columns = [c.strip().lower() for c in df.columns]
    logger.debug("Normalizing %s with columns %s", csv_path, original_cols)

    # Map columns to canonical names
    mapped_cols = {col: COLUMN_MAP.get(col, col) for col in df.columns}
    df = df.rename(columns=mapped_cols)

    # Filter Pernambuco
    if "uf" in df.columns:
        df = df[df["uf"].astype(str).str.upper() == "PE"]
    else:
        logger.warning("Column 'UF' not found in %s; keeping all rows", csv_path)

    # Handle date/time
    if "datehour" in df.columns:
        df["timestamp"] = pd.to_datetime(df["datehour"], errors="coerce")
        df["date"] = df["timestamp"].dt.date
        df["hour_utc"] = df["timestamp"].dt.strftime("%H:%M")
    else:
        df["date"] = pd.to_datetime(df.get("date"), errors="coerce").dt.date
        if "hour_utc" not in df.columns:
            df["hour_utc"] = "00:00"
    df = df.drop(columns=[c for c in ["timestamp", "datehour"] if c in df.columns])

    # Enforce numeric types
    numeric_cols = [
        "temp_ins_c",
        "temp_max_c",
        "temp_min_c",
        "humidity",
        "wind_speed",
        "radiation",
        "precipitation",
        "latitude",
        "longitude",
        "altitude",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure required columns exist
    for col in REQUIRED_BASE_COLUMNS:
        if col not in df.columns:
            df[col] = None

    normalized = df[REQUIRED_BASE_COLUMNS].dropna(subset=["date", "hour_utc", "station_code"])
    logger.info("Normalized %s rows from %s", len(normalized), csv_path)
    return normalized.reset_index(drop=True)


__all__ = ["normalize_csv", "REQUIRED_BASE_COLUMNS"]
