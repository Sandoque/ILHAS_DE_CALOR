"""
Load normalized MapBiomas data into aux_cobertura_vegetal_pe table.

Performs:
  1. Lookup id_cidade from dim_cidade_pe using geocode
  2. Pivot class categories (vegetacao_urbana, area_construida, corpos_dagua) into columns
  3. Calculate percentages (area as %)
  4. INSERT ... ON CONFLICT (id_cidade, ano) DO UPDATE
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text

from etl.utils.constants import DATABASE_URL
from etl.utils.logger import get_logger

logger = get_logger(__name__)

TARGET_TABLE = "aux_cobertura_vegetal_pe"
TARGET_SCHEMA = "public"


def _prepare_data_for_loading(df: pd.DataFrame, engine) -> pd.DataFrame:
    """
    Transform normalized MapBiomas data to aux_cobertura_vegetal_pe schema.
    
    Input: geocode, municipality, year, class_category, area
    Output: id_cidade, ano, perc_vegetacao_urbana, perc_area_construida, perc_corpos_dagua, fonte
    """
    if df.empty:
        logger.warning("Empty dataframe provided")
        return df.iloc[0:0]
    
    # Fetch geocode -> id_cidade mapping
    try:
        query = text("SELECT id_cidade, codigo_ibge FROM dim_cidade_pe WHERE codigo_ibge IS NOT NULL")
        with engine.connect() as conn:
            result = conn.execute(query)
            geocode_map = {int(row[1]): int(row[0]) for row in result if row[1] is not None}
        logger.info("Loaded mapping for %s cities", len(geocode_map))
    except Exception as e:
        logger.exception("Failed to fetch city mapping: %s", e)
        return df.iloc[0:0]
    
    # Add id_cidade
    df = df.copy()
    df["id_cidade"] = df["geocode"].map(geocode_map)
    
    # Drop rows without city mapping
    initial_count = len(df)
    df = df.dropna(subset=["id_cidade"])
    if len(df) < initial_count:
        logger.warning("Dropped %s rows due to unmapped geocodes", initial_count - len(df))
    
    df["id_cidade"] = df["id_cidade"].astype(int)
    df = df.rename(columns={"year": "ano"})
    
    # Pivot class_category to columns
    pivot_df = df.pivot_table(
        index=["id_cidade", "ano"],
        columns="class_category",
        values="area",
        aggfunc="sum",
    ).reset_index()
    
    # Rename to match schema (normalize column names)
    rename_map = {
        "vegetacao_urbana": "perc_vegetacao_urbana",
        "area_construida": "perc_area_construida",
        "corpos_dagua": "perc_corpos_dagua",
    }
    pivot_df = pivot_df.rename(columns=rename_map)
    
    # Ensure all columns exist (fill missing with 0)
    for col in ["perc_vegetacao_urbana", "perc_area_construida", "perc_corpos_dagua"]:
        if col not in pivot_df.columns:
            pivot_df[col] = 0.0
    
    # Add source metadata
    pivot_df["fonte"] = "MapBiomas v10"
    
    return pivot_df[["id_cidade", "ano", "perc_vegetacao_urbana", "perc_area_construida", "perc_corpos_dagua", "fonte"]]


def load_mapbiomas(df: pd.DataFrame) -> None:
    """
    Load normalized MapBiomas data into aux_cobertura_vegetal_pe.
    
    Uses UPSERT logic: INSERT ... ON CONFLICT (id_cidade, ano) DO UPDATE
    """
    if df.empty:
        logger.warning("No MapBiomas data to load")
        return
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured")
    
    engine = create_engine(DATABASE_URL)
    
    # Prepare data
    load_df = _prepare_data_for_loading(df, engine)
    
    if load_df.empty:
        logger.warning("No data to load after transformation")
        return
    
    logger.info("Loading %s rows into %s.%s", len(load_df), TARGET_SCHEMA, TARGET_TABLE)
    
    with engine.begin() as conn:
        try:
            # Use raw SQL for UPSERT
            # Build INSERT ... ON CONFLICT query
            insert_sql = f"""
            INSERT INTO {TARGET_SCHEMA}.{TARGET_TABLE} 
            (id_cidade, ano, perc_vegetacao_urbana, perc_area_construida, perc_corpos_dagua, fonte)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_cidade, ano) DO UPDATE SET
                perc_vegetacao_urbana = EXCLUDED.perc_vegetacao_urbana,
                perc_area_construida = EXCLUDED.perc_area_construida,
                perc_corpos_dagua = EXCLUDED.perc_corpos_dagua,
                fonte = EXCLUDED.fonte
            """
            
            # Convert to tuples and insert
            data_tuples = [
                (
                    row["id_cidade"],
                    row["ano"],
                    row["perc_vegetacao_urbana"],
                    row["perc_area_construida"],
                    row["perc_corpos_dagua"],
                    row["fonte"],
                )
                for _, row in load_df.iterrows()
            ]
            
            # Execute in batches
            batch_size = 1000
            for i in range(0, len(data_tuples), batch_size):
                batch = data_tuples[i : i + batch_size]
                logger.debug("Inserting batch %d of %d", i // batch_size + 1, (len(data_tuples) + batch_size - 1) // batch_size)
                
                # Use executemany for batch insert (simulated via individual inserts due to SQLAlchemy)
                # For better performance, consider using raw psycopg2 connection
                for data in batch:
                    conn.execute(text(insert_sql), data)
            
            logger.info("Successfully loaded %s rows into %s", len(load_df), TARGET_TABLE)
        except Exception:
            logger.exception("Failed to load MapBiomas data")
            raise


__all__ = ["load_mapbiomas", "TARGET_TABLE", "TARGET_SCHEMA"]
