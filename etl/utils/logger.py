"""
Shared application logger for ETL module.

Provides get_logger() helper that configures a console logger with level from
LOG_LEVEL environment variable (default INFO). All modules should import and use
this logger to keep log formatting consistent.
"""
from __future__ import annotations

import logging
import os
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a configured logger.

    Ensures loggers are consistently configured with a stream handler. Logging
    level can be controlled via LOG_LEVEL environment variable.
    """
    logger_name = name or "etl"
    logger = logging.getLogger(logger_name)

    if logger.handlers:
        return logger

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    logger.debug("Logger initialized with level %s", level_name)
    return logger


__all__ = ["get_logger"]
