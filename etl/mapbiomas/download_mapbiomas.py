"""Download MapBiomas XLSX file."""
from __future__ import annotations

from pathlib import Path

from etl.utils.constants import DATA_DIR
from etl.utils.file_management import download_file, ensure_dir
from etl.utils.logger import get_logger

logger = get_logger(__name__)

MAPBIOMAS_URL = (
    "https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_10/"
    "lulc/statistics/MAPBIOMAS_BRAZIL-COL.10-BIOME_STATE_MUNICIPALITY.xlsx"
)

RAW_DIR = DATA_DIR.parent / "mapbiomas" / "raw"


def download_xlsx() -> Path:
    """Download the MapBiomas XLSX to raw directory."""
    ensure_dir(RAW_DIR)
    dest = RAW_DIR / "MAPBIOMAS_BRAZIL-COL10.xlsx"
    logger.info("Downloading MapBiomas XLSX to %s", dest)
    return download_file(MAPBIOMAS_URL, dest)


__all__ = ["download_xlsx", "MAPBIOMAS_URL", "RAW_DIR"]
