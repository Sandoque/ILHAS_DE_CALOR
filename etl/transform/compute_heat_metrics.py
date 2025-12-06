"""
Compute heat-related metrics on normalized climate data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from etl.utils.logger import get_logger

logger = get_logger(__name__)


def _apparent_temperature(temp_c: pd.Series, humidity: pd.Series, wind_speed: pd.Series) -> pd.Series:
    """Calculate apparent temperature using Steadman equation."""
    e = (humidity / 100.0) * 6.105 * np.exp(17.27 * temp_c / (237.7 + temp_c))
    return temp_c + 0.33 * e - 0.70 * wind_speed - 4.00


def _heat_index(temp_c: pd.Series, humidity: pd.Series) -> pd.Series:
    """Compute NOAA heat index in Celsius."""
    temp_f = temp_c * 9 / 5 + 32
    hi_f = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * humidity
        - 0.22475541 * temp_f * humidity
        - 0.00683783 * temp_f**2
        - 0.05481717 * humidity**2
        + 0.00122874 * temp_f**2 * humidity
        + 0.00085282 * temp_f * humidity**2
        - 0.00000199 * temp_f**2 * humidity**2
    )
    hi_c = (hi_f - 32) * 5 / 9
    # Only apply when heat conditions make sense; otherwise use actual temperature
    return hi_c.where((temp_c >= 26) & (humidity >= 40), temp_c)


def add_heat_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add heat metrics columns to a normalized dataframe."""
    required = ["temp_ins_c", "temp_max_c", "temp_min_c", "humidity", "wind_speed"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for heat metrics: {missing}")

    df = df.copy()
    df["apparent_temperature"] = _apparent_temperature(df["temp_ins_c"], df["humidity"], df["wind_speed"])
    df["heat_index"] = _heat_index(df["temp_ins_c"], df["humidity"])
    df["thermal_amplitude"] = df["temp_max_c"] - df["temp_min_c"]

    # Rolling 7-day mean of apparent temperature per station
    df["timestamp"] = pd.to_datetime(df["date"].astype(str) + " " + df["hour_utc"].astype(str), errors="coerce")
    df = df.sort_values(["station_code", "timestamp"])
    df["rolling_heat_7d"] = (
        df.groupby("station_code")
        .rolling("7D", on="timestamp")["apparent_temperature"]
        .mean()
        .reset_index(level=0, drop=True)
    )
    df = df.drop(columns=["timestamp"])
    logger.info("Computed heat metrics for %s rows", len(df))
    return df


__all__ = ["add_heat_metrics"]
