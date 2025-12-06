"""
Load dataframes into PostgreSQL using SQLAlchemy.
"""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from etl.utils.constants import DATABASE_URL, TARGET_SCHEMA, TARGET_TABLE
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def _get_engine(database_url: Optional[str] = None) -> Engine:
    url = database_url or DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is not set")
    return create_engine(url)


def load_dataframe(df: pd.DataFrame, engine: Optional[Engine] = None, chunksize: int = 5000) -> None:
    """Append dataframe into target PostgreSQL table."""
    eng = engine or _get_engine()
    logger.info("Loading %s rows into %s.%s", len(df), TARGET_SCHEMA, TARGET_TABLE)
    try:
        df.to_sql(
            TARGET_TABLE,
            eng,
            schema=TARGET_SCHEMA,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=chunksize,
        )
    except Exception:
        logger.exception("Failed to load data into %s.%s", TARGET_SCHEMA, TARGET_TABLE)
        raise


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
