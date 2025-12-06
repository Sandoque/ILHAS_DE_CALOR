"""Simulation endpoints."""
from __future__ import annotations

from flask import Blueprint, request

from ..services.simulation_service import (
    simulate_future_heat_scenario,
    simulate_rainfall_change,
    simulate_temperature_increase,
)
from ..utils.responses import error, success

bp = Blueprint("api_simulation", __name__, url_prefix="/api/simulation")


def _payload() -> dict:
    if request.is_json:
        return request.get_json(silent=True) or {}
    if request.form:
        data = request.form.to_dict(flat=True)
        climate_vars = {
            k.split("[")[1].split("]")[0]: float(v) if v else 0
            for k, v in data.items()
            if k.startswith("climate_variables[")
        }
        data["climate_variables"] = climate_vars
        return data
    return {}


@bp.post("/temperature")
def simulate_temperature():
    payload = _payload()
    station_code = payload.get("station_code")
    percentage = payload.get("percentage", 0)
    if not station_code:
        return error("station_code is required", status=400)
    data = simulate_temperature_increase(station_code, float(percentage))
    return success(data)


@bp.post("/rainfall")
def simulate_rainfall():
    payload = _payload()
    station_code = payload.get("station_code")
    delta_mm = float(payload.get("delta_mm", 0))
    if not station_code:
        return error("station_code is required", status=400)
    data = simulate_rainfall_change(station_code, delta_mm)
    return success(data)


@bp.post("/future")
def simulate_future():
    payload = _payload()
    station_code = payload.get("station_code")
    climate_variables = payload.get("climate_variables", {}) or {}
    if not station_code:
        return error("station_code is required", status=400)
    data = simulate_future_heat_scenario(station_code, climate_variables)
    return success(data)
