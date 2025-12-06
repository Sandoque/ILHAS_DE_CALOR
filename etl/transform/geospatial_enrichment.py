"""
Geospatial enrichment utilities.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

from etl.utils.logger import get_logger

logger = get_logger(__name__)


def _mock_ibge_lookup(latitude: float, longitude: float) -> str:
    """Mock lookup that returns a placeholder municipality name."""
    if pd.isna(latitude) or pd.isna(longitude):
        return "Unknown"
    return "Municipio Desconhecido"


def enrich_with_geospatial(df: pd.DataFrame) -> pd.DataFrame:
    """Add municipality information using station coordinates.

    TODO: Integrate IBGE API to map latitude/longitude to municipality codes.
    This placeholder uses a deterministic mock to allow downstream processing.
    """
    df = df.copy()
    df["municipality"] = df.apply(
        lambda row: _mock_ibge_lookup(row.get("latitude"), row.get("longitude")), axis=1
    )
    logger.info("Enriched geospatial data for %s rows", len(df))
    return df


__all__ = ["enrich_with_geospatial"]
