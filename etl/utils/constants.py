"""
Global constants and environment configuration for the ETL.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Final, List

# Environment-driven configuration
INMET_BASE_URL: Final[str] = os.getenv(
    "INMET_BASE_URL", "https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"
)
DATA_DIR: Final[Path] = Path(os.getenv("DATA_DIR", "data/inmet"))
RAW_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DIR: Final[Path] = DATA_DIR / "processed"
DATABASE_URL: Final[str | None] = os.getenv("DATABASE_URL")

# Data defaults
START_YEAR: Final[int] = int(os.getenv("START_YEAR", "1961"))
END_YEAR: Final[int] = int(os.getenv("END_YEAR", "2024"))

# Database targets
TARGET_SCHEMA: Final[str] = "public"
TARGET_TABLE: Final[str] = "climate_hourly"

CANONICAL_COLUMNS: Final[List[str]] = [
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
    "datetime_utc",
    "datetime_local",
    "apparent_temperature",
    "heat_index",
    "thermal_amplitude",
    "rolling_heat_7d",
    "municipality",
]


__all__ = [
    "INMET_BASE_URL",
    "DATA_DIR",
    "RAW_DIR",
    "PROCESSED_DIR",
    "DATABASE_URL",
    "TARGET_SCHEMA",
    "TARGET_TABLE",
    "CANONICAL_COLUMNS",
    "START_YEAR",
    "END_YEAR",
]
