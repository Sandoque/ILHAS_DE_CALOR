"""Station API endpoints."""
from __future__ import annotations

from flask import Blueprint

from ..services.station_service import get_station_details, list_stations
from ..utils.responses import error, success

bp = Blueprint("api_stations", __name__, url_prefix="/api/stations")


@bp.get("")
def stations():
    return success(list_stations())


@bp.get("/<code>")
def station_detail(code: str):
    data = get_station_details(code)
    if not data:
        return error("Station not found", status=404)
    return success(data)
