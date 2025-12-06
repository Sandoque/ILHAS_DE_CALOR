"""
Utility to list expected INMET source years.
"""
from __future__ import annotations

from datetime import datetime
from typing import List

from etl.utils.constants import END_YEAR, START_YEAR
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def expected_years(start: int | None = None, end: int | None = None) -> List[int]:
    """Return a list of expected years between start and end inclusive."""
    current_year = datetime.utcnow().year
    _start = start or START_YEAR
    _end = min(end or END_YEAR, current_year)
    if _end < _start:
        logger.warning("End year %s is before start year %s; swapping.", _end, _start)
        _start, _end = _end, _start
    return list(range(_start, _end + 1))


__all__ = ["expected_years"]
