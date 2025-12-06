"""
Download INMET historical ZIP archives for a given year.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from etl.utils.constants import INMET_BASE_URL, RAW_DIR
from etl.utils.file_management import download_file, ensure_dir
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def build_url(year: int) -> str:
    """Build the download URL for a given year."""
    return INMET_BASE_URL.format(year=year)


def download_year(year: int) -> Path:
    """Download the ZIP file for a specific year and return the path."""
    ensure_dir(RAW_DIR)
    url = build_url(year)
    dest = RAW_DIR / f"{year}.zip"
    logger.info("Downloading INMET archive for year %s", year)
    return download_file(url, dest)


def download_years(years: List[int]) -> List[Path]:
    """Download multiple years and return list of paths."""
    paths: List[Path] = []
    for year in years:
        try:
            path = download_year(year)
            paths.append(path)
        except Exception:
            logger.exception("Skipping year %s due to download error", year)
    return paths


__all__ = ["download_year", "download_years", "build_url"]
