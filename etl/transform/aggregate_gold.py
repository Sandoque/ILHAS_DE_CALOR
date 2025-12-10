"""
Aggregate bronze climate data to daily GOLD metrics by city.

Transforms hourly bronze_clima_pe_horario data into daily aggregates
with heat risk classification.
"""
from __future__ import annotations

import pandas as pd
import numpy as np

from etl.utils.logger import get_logger

logger = get_logger(__name__)


def classify_heat_risk(heat_index_max: float) -> str:
    """
    Classify heat risk based on maximum heat index.
    
    Rules:
        HI < 27       → "Baixo"
        27–32         → "Moderado"
        33–40         → "Alto"
        41–52         → "Muito Alto"
        > 52          → "Extremo"
    """
    if pd.isna(heat_index_max):
        return "Desconhecido"
    
    hi = float(heat_index_max)
    
    if hi < 27:
        return "Baixo"
    elif hi < 33:
        return "Moderado"
    elif hi < 41:
        return "Alto"
    elif hi <= 52:
        return "Muito Alto"
    else:
        return "Extremo"


def aggregate_daily(df_bronze: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate hourly bronze climate data to daily GOLD metrics by city.
    
    Input columns expected from bronze_clima_pe_horario:
        - id_estacao or id_cidade
        - data_hora_utc (or datetime_utc)
        - temp_ar_c
        - temp_max_ant, temp_min_ant
        - umid_rel_pct
        - precipitacao_mm
        - radiacao_kj_m2
        - apparent_temperature
        - heat_index
        - rolling_heat_7d
    
    Output: DataFrame with daily aggregates by id_cidade + data
    """
    if df_bronze.empty:
        logger.warning("Empty bronze dataframe provided")
        return df_bronze.iloc[0:0]
    
    df = df_bronze.copy()
    
    # Normalize column names (handle different naming conventions)
    column_rename = {
        "datetime_utc": "data_hora_utc",
        "data_hora_utc": "data_hora_utc",
    }
    df = df.rename(columns=column_rename)
    
    # Ensure datetime is properly typed
    if "data_hora_utc" in df.columns:
        df["data_hora_utc"] = pd.to_datetime(df["data_hora_utc"], errors="coerce")
        df["data"] = df["data_hora_utc"].dt.date
    elif "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.date
    else:
        logger.error("No date column found in bronze data")
        return df.iloc[0:0]
    
    # Ensure we have id_cidade (from id_estacao lookup if needed)
    if "id_cidade" not in df.columns and "id_estacao" in df.columns:
        logger.warning("Using id_estacao as id_cidade (no proper join available)")
        df["id_cidade"] = df["id_estacao"]
    elif "id_cidade" not in df.columns:
        logger.error("No id_cidade or id_estacao column found")
        return df.iloc[0:0]
    
    # Map column names from bronze schema
    column_mapping = {
        "temp_ar_c": "temperatura",
        "temperature": "temperatura",
        "temp_max_ant": "temp_max",
        "temp_max_c": "temp_max",
        "temp_min_ant": "temp_min",
        "temp_min_c": "temp_min",
        "umid_rel_pct": "umidade",
        "humidity": "umidade",
        "precipitacao_mm": "precipitacao",
        "precipitation": "precipitacao",
        "radiacao_kj_m2": "radiacao",
        "radiation": "radiacao",
        "apparent_temperature": "aparente",
        "heat_index": "heat_index",
        "rolling_heat_7d": "rolling_heat_7d",
    }
    
    df = df.rename(columns=column_mapping)
    
    # Ensure numeric types
    numeric_cols = [
        "temperatura",
        "temp_max",
        "temp_min",
        "umidade",
        "precipitacao",
        "radiacao",
        "aparente",
        "heat_index",
        "rolling_heat_7d",
    ]
    
    # Replace common sentinel values
    df.replace({-9999: pd.NA, -9999.0: pd.NA, -99999: pd.NA, -99999.0: pd.NA}, inplace=True)

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            # Drop gross outliers to protect DB precision (abs < 1000)
            df[col] = df[col].where(df[col].abs() < 1000)
            if col in {"precipitacao", "radiacao", "umidade"}:
                df[col] = df[col].where(df[col] >= 0)
            if col == "umidade":
                df[col] = df[col].where(df[col] <= 100)
    
    # Aggregate by id_cidade + data
    agg_dict = {
        "temperatura": "mean",
        "temp_max": "max",
        "temp_min": "min",
        "umidade": "mean",
        "precipitacao": "sum",
        "radiacao": "sum",
        "aparente": "mean",
        "heat_index": "max",
        "rolling_heat_7d": "mean",
    }
    
    # Remove keys that don't exist in dataframe
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
    
    gold_df = df.groupby(["id_cidade", "data"]).agg(agg_dict).reset_index()
    
    # Rename aggregated columns to match GOLD schema
    rename_map = {
        "temperatura": "temp_media",
        "temp_max": "temp_max",
        "temp_min": "temp_min",
        "umidade": "umidade_media",
        "precipitacao": "precipitacao_total",
        "radiacao": "radiacao_total",
        "aparente": "aparente_media",
        "heat_index": "heat_index_max",
        "rolling_heat_7d": "rolling_heat_7d",
    }
    
    gold_df = gold_df.rename(columns=rename_map)
    
    # Calculate thermal amplitude
    if "temp_max" in gold_df.columns and "temp_min" in gold_df.columns:
        gold_df["amplitude_termica"] = gold_df["temp_max"] - gold_df["temp_min"]
    
    # Classify heat risk based on heat_index_max
    if "heat_index_max" in gold_df.columns:
        gold_df["risco_calor"] = gold_df["heat_index_max"].apply(classify_heat_risk)
    else:
        gold_df["risco_calor"] = "Desconhecido"

    # Final sanity checks against schema constraints
    limits_5_2 = ["temp_media", "temp_max", "temp_min", "umidade_media", "amplitude_termica", "aparente_media", "heat_index_max", "rolling_heat_7d"]
    for col in limits_5_2:
        if col in gold_df.columns:
            gold_df[col] = pd.to_numeric(gold_df[col], errors="coerce")
            gold_df[col] = gold_df[col].where(gold_df[col].abs() < 1000)
            if col == "umidade_media":
                gold_df[col] = gold_df[col].where((gold_df[col] >= 0) & (gold_df[col] <= 100))
    if "precipitacao_total" in gold_df.columns:
        gold_df["precipitacao_total"] = pd.to_numeric(gold_df["precipitacao_total"], errors="coerce")
        gold_df["precipitacao_total"] = gold_df["precipitacao_total"].where(gold_df["precipitacao_total"] >= 0)
    if "radiacao_total" in gold_df.columns:
        gold_df["radiacao_total"] = pd.to_numeric(gold_df["radiacao_total"], errors="coerce")
        gold_df["radiacao_total"] = gold_df["radiacao_total"].where(gold_df["radiacao_total"] >= 0)
    
    # Ensure all expected columns exist
    expected_cols = [
        "id_cidade",
        "data",
        "temp_media",
        "temp_max",
        "temp_min",
        "umidade_media",
        "precipitacao_total",
        "radiacao_total",
        "amplitude_termica",
        "aparente_media",
        "heat_index_max",
        "rolling_heat_7d",
        "risco_calor",
    ]
    
    for col in expected_cols:
        if col not in gold_df.columns:
            gold_df[col] = None
    
    # Select only expected columns in correct order
    gold_df = gold_df[expected_cols]
    
    logger.info(
        "Aggregated %s hourly records to %s daily GOLD records",
        len(df),
        len(gold_df),
    )
    
    return gold_df


__all__ = ["aggregate_daily", "classify_heat_risk"]
