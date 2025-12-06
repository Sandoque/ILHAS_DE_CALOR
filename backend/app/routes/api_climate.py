"""Climate-related API endpoints."""
from __future__ import annotations

from flask import Blueprint, request

from ..services.climate_service import (
    compute_trends,
    get_climate_by_station,
    get_daily_summary,
    list_years_available,
)
from ..utils.responses import error, success

bp = Blueprint("api_climate", __name__, url_prefix="/api/climate")


@bp.get("/station/<code>")
def climate_by_station(code: str):
    start = request.args.get("start")
    end = request.args.get("end")
    data = get_climate_by_station(code, start, end)
    return success(data)


@bp.get("/station/<code>/daily")
def climate_daily(code: str):
    try:
        limit = int(request.args.get("limit", 30))
    except Exception:
        limit = 30
    data = get_daily_summary(code, limit)
    return success(data)


@bp.get("/years")
def climate_years():
    data = list_years_available()
    return success(data)


@bp.get("/<code>/trends")
def climate_trends(code: str):
    data = compute_trends(code)
    if not data:
        return error("Station not found or no data", status=404)
    return success(data)
