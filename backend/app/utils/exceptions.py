"""Custom exceptions for API responses."""
from __future__ import annotations

from typing import Optional


class APIError(Exception):
    """Generic API error with HTTP status."""

    def __init__(self, message: str, status_code: int = 400, payload: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> dict:
        data = dict(self.payload)
        data["message"] = self.message
        return data


__all__ = ["APIError"]
