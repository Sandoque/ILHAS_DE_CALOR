"""Analytics API endpoints."""
from __future__ import annotations

from flask import Blueprint, request

from ..services.analytics_service import (
    compute_heat_alerts,
    compute_rank_hottest_stations,
    compute_statewide_heat_map,
)
from ..utils.responses import error, success

bp = Blueprint("api_analytics", __name__, url_prefix="/api/analytics")


@bp.get("/heatmap/<date>")
def heatmap(date: str):
    data = compute_statewide_heat_map(date)
    return success(data)


@bp.get("/hottest")
def hottest():
    try:
        limit = int(request.args.get("limit", 10))
    except Exception:
        limit = 10
    data = compute_rank_hottest_stations(limit)
    return success(data)


@bp.get("/alerts")
def alerts():
    try:
        threshold = float(request.args.get("threshold", 40.0))
    except Exception:
        return error("Invalid threshold", status=400)
    data = compute_heat_alerts(threshold)
    return success(data)
