"""
Extraction helpers for INMET ZIP archives.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from etl.utils.constants import RAW_DIR, PROCESSED_DIR
from etl.utils.file_management import ensure_dir, extract_zip
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def extract_year_zip(zip_path: Path) -> Path:
    """Extract a yearly INMET ZIP file into the processed directory."""
    target_dir = PROCESSED_DIR / zip_path.stem
    ensure_dir(target_dir)
    try:
        extract_zip(zip_path, target_dir)
        logger.info("Extracted %s to %s", zip_path, target_dir)
        return target_dir
    except Exception:
        logger.exception("Failed to extract %s", zip_path)
        raise


def list_extracted_csvs(year_dir: Path) -> List[Path]:
    """List CSV files inside an extracted year directory."""
    return [
        p
        for p in year_dir.rglob("*")
        if p.is_file() and p.suffix.lower() == ".csv"
    ]


__all__ = ["extract_year_zip", "list_extracted_csvs"]
