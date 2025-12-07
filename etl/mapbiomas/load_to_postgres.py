"""Load normalized MapBiomas data into PostgreSQL."""
from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text

from etl.utils.constants import DATABASE_URL
from etl.utils.logger import get_logger

logger = get_logger(__name__)

TARGET_TABLE = "mapbiomas_coverage"
TARGET_SCHEMA = "public"


def load_mapbiomas(df: pd.DataFrame) -> None:
    if df.empty:
        logger.warning("No MapBiomas data to load")
        return
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured")
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        logger.info("Truncating %s.%s", TARGET_SCHEMA, TARGET_TABLE)
        conn.execute(text(f"TRUNCATE TABLE {TARGET_SCHEMA}.{TARGET_TABLE};"))
        logger.info("Loading %s rows into %s.%s", len(df), TARGET_SCHEMA, TARGET_TABLE)
        df.to_sql(
            TARGET_TABLE,
            conn,
            schema=TARGET_SCHEMA,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000,
        )


__all__ = ["load_mapbiomas", "TARGET_TABLE", "TARGET_SCHEMA"]
