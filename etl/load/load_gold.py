"""
Load GOLD climate metrics into PostgreSQL with UPSERT logic.

Loads aggregated daily climate data into gold_clima_pe_diario table
using INSERT ... ON CONFLICT for idempotent updates.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from etl.utils.constants import DATABASE_URL
from etl.utils.logger import get_logger

logger = get_logger(__name__)

TARGET_TABLE = "gold_clima_pe_diario"
TARGET_SCHEMA = "public"


def _get_engine(database_url: Optional[str] = None) -> Engine:
    """Get SQLAlchemy engine from DATABASE_URL."""
    url = database_url or DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is not set")
    return create_engine(url)


def load_gold(df_gold: pd.DataFrame, engine: Optional[Engine] = None) -> None:
    """
    Load GOLD daily metrics into gold_clima_pe_diario with UPSERT logic.
    
    Performs:
        INSERT INTO gold_clima_pe_diario (...)
        VALUES (...)
        ON CONFLICT (id_cidade, data)
        DO UPDATE SET ... = EXCLUDED...
    
    Args:
        df_gold: DataFrame with columns:
            - id_cidade
            - data
            - temp_media, temp_max, temp_min
            - umidade_media
            - precipitacao_total
            - radiacao_total
            - amplitude_termica
            - aparente_media
            - heat_index_max
            - rolling_heat_7d
            - risco_calor
        engine: SQLAlchemy engine (optional, defaults to DATABASE_URL)
    """
    if df_gold.empty:
        logger.warning("No GOLD data to load")
        return
    
    eng = engine or _get_engine()
    
    # Ensure data types
    df_gold = df_gold.copy()
    df_gold["id_cidade"] = df_gold["id_cidade"].astype(int)
    df_gold["data"] = pd.to_datetime(df_gold["data"]).dt.date
    
    # Fill NaN values with None for SQL NULL
    df_gold = df_gold.where(pd.notna(df_gold), None)
    
    logger.info("Preparing to load %s GOLD records into %s.%s", len(df_gold), TARGET_SCHEMA, TARGET_TABLE)
    
    with eng.begin() as conn:
        try:
            # Build UPSERT query using raw SQL
            insert_sql = f"""
            INSERT INTO {TARGET_SCHEMA}.{TARGET_TABLE} (
                id_cidade, data, temp_media, temp_max, temp_min, umidade_media,
                precipitacao_total, radiacao_total, amplitude_termica,
                aparente_media, heat_index_max, rolling_heat_7d, risco_calor
            )
            VALUES (
                :id_cidade, :data, :temp_media, :temp_max, :temp_min, :umidade_media,
                :precipitacao_total, :radiacao_total, :amplitude_termica,
                :aparente_media, :heat_index_max, :rolling_heat_7d, :risco_calor
            )
            ON CONFLICT (id_cidade, data)
            DO UPDATE SET
                temp_media = EXCLUDED.temp_media,
                temp_max = EXCLUDED.temp_max,
                temp_min = EXCLUDED.temp_min,
                umidade_media = EXCLUDED.umidade_media,
                precipitacao_total = EXCLUDED.precipitacao_total,
                radiacao_total = EXCLUDED.radiacao_total,
                amplitude_termica = EXCLUDED.amplitude_termica,
                aparente_media = EXCLUDED.aparente_media,
                heat_index_max = EXCLUDED.heat_index_max,
                rolling_heat_7d = EXCLUDED.rolling_heat_7d,
                risco_calor = EXCLUDED.risco_calor;
            """
            
            # Insert records in batches
            batch_size = 1000
            total_inserted = 0
            
            for i in range(0, len(df_gold), batch_size):
                batch = df_gold.iloc[i : i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(df_gold) + batch_size - 1) // batch_size
                
                logger.debug(
                    "Processing batch %d of %d (%d records)",
                    batch_num,
                    total_batches,
                    len(batch),
                )
                
                # Convert batch to list of dicts for parameterized query
                for _, row in batch.iterrows():
                    try:
                        conn.execute(
                            text(insert_sql),
                            {
                                "id_cidade": int(row["id_cidade"]),
                                "data": row["data"],
                                "temp_media": float(row["temp_media"]) if pd.notna(row["temp_media"]) else None,
                                "temp_max": float(row["temp_max"]) if pd.notna(row["temp_max"]) else None,
                                "temp_min": float(row["temp_min"]) if pd.notna(row["temp_min"]) else None,
                                "umidade_media": float(row["umidade_media"]) if pd.notna(row["umidade_media"]) else None,
                                "precipitacao_total": float(row["precipitacao_total"]) if pd.notna(row["precipitacao_total"]) else None,
                                "radiacao_total": float(row["radiacao_total"]) if pd.notna(row["radiacao_total"]) else None,
                                "amplitude_termica": float(row["amplitude_termica"]) if pd.notna(row["amplitude_termica"]) else None,
                                "aparente_media": float(row["aparente_media"]) if pd.notna(row["aparente_media"]) else None,
                                "heat_index_max": float(row["heat_index_max"]) if pd.notna(row["heat_index_max"]) else None,
                                "rolling_heat_7d": float(row["rolling_heat_7d"]) if pd.notna(row["rolling_heat_7d"]) else None,
                                "risco_calor": str(row["risco_calor"]) if pd.notna(row["risco_calor"]) else None,
                            },
                        )
                        total_inserted += 1
                    except Exception as e:
                        logger.error("Error inserting row for id_cidade=%s, data=%s: %s", row["id_cidade"], row["data"], e)
                        continue
            
            logger.info(
                "Successfully loaded %d of %d GOLD records into %s.%s",
                total_inserted,
                len(df_gold),
                TARGET_SCHEMA,
                TARGET_TABLE,
            )
            
            if total_inserted < len(df_gold):
                logger.warning("Failed to insert %d records", len(df_gold) - total_inserted)
        
        except Exception:
            logger.exception("Failed to load GOLD data")
            raise


__all__ = ["load_gold", "TARGET_TABLE", "TARGET_SCHEMA"]
