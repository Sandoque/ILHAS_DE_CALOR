"""Application configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass
class Config:
    """Base configuration."""

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "postgresql://ilhas_user:ilhas_pass@localhost:5433/ilhas_de_calor"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    DEBUG: bool = _bool(os.getenv("DEBUG"), False)


def get_config() -> Config:
    """Return config object (simple for now, but can expand by env)."""
    return Config()


__all__ = ["Config", "get_config"]
