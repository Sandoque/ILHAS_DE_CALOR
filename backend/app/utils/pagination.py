"""Pagination helpers for SQLAlchemy queries."""
from __future__ import annotations

from typing import Any, Dict

from flask import request


def paginate_query(query, default_page: int = 1, default_per_page: int = 20) -> Dict[str, Any]:
    """Paginate a SQLAlchemy query using request args if available."""
    try:
        page = int(request.args.get("page", default_page))
        per_page = int(request.args.get("per_page", default_per_page))
    except Exception:
        page, per_page = default_page, default_per_page

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": pagination.items,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
