"""
Timing utilities for measuring ETL step duration.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from .logger import get_logger

logger = get_logger(__name__)


@contextmanager
def time_block(task_name: str) -> Iterator[None]:
    """Context manager to log the duration of a block."""
    start = time.perf_counter()
    logger.info("Starting %s", task_name)
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        logger.info("Finished %s in %.2f seconds", task_name, duration)
