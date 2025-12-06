"""
Reusable file utilities for ETL.
"""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Optional

import requests

from .logger import get_logger

logger = get_logger(__name__)


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists and return the path."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to create directory %s: %s", path, exc)
        raise


def download_file(url: str, dest: Path, timeout: int = 60) -> Path:
    """Download a file to the destination path."""
    logger.info("Downloading %s to %s", url, dest)
    ensure_dir(dest.parent)
    try:
        with requests.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()
            with dest.open("wb") as fout:
                shutil.copyfileobj(response.raw, fout)
        logger.info("Downloaded %s (%s bytes)", dest, dest.stat().st_size)
        return dest
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to download %s: %s", url, exc)
        raise


def extract_zip(zip_path: Path, target_dir: Path) -> Path:
    """Extract a ZIP file into target_dir and return path."""
    ensure_dir(target_dir)
    logger.info("Extracting %s to %s", zip_path, target_dir)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_dir)
        return target_dir
    except zipfile.BadZipFile as exc:  # pragma: no cover
        logger.error("Invalid zip file %s: %s", zip_path, exc)
        raise
    except Exception as exc:  # pragma: no cover
        logger.error("Failed to extract %s: %s", zip_path, exc)
        raise
