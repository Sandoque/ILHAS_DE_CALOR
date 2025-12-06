"""Simulation helpers for what-if scenarios."""
from __future__ import annotations

from typing import Dict, List

from ..models import ClimateHourly, ClimateHourlySchema

schema_many = ClimateHourlySchema(many=True)


def _recent_data(station_code: str, limit: int = 100) -> List[dict]:
    records = (
        ClimateHourly.query.filter_by(station_code=station_code)
        .order_by(ClimateHourly.datetime_utc.desc())
        .limit(limit)
        .all()
    )
    return schema_many.dump(records)


def simulate_temperature_increase(station_code: str, percentage: float) -> List[dict]:
    factor = 1 + (percentage or 0) / 100.0
    data = _recent_data(station_code)
    for row in data:
        for field in ["temperature", "apparent_temperature", "heat_index"]:
            if row.get(field) is not None:
                row[field] = row[field] * factor
    return data


def simulate_rainfall_change(station_code: str, delta_mm: float) -> List[dict]:
    data = _recent_data(station_code)
    for row in data:
        if row.get("precipitation") is not None:
            row["precipitation"] = max(0, row["precipitation"] + delta_mm)
    return data


def simulate_future_heat_scenario(station_code: str, climate_variables: Dict[str, float]) -> List[dict]:
    data = _recent_data(station_code)
    temp_delta = climate_variables.get("temperature", 0)
    humidity_delta = climate_variables.get("humidity", 0)
    wind_delta = climate_variables.get("wind_speed", 0)
    precip_delta = climate_variables.get("precipitation", 0)
    for row in data:
        if row.get("temperature") is not None:
            row["temperature"] += temp_delta
        if row.get("humidity") is not None:
            row["humidity"] = max(0, min(100, row["humidity"] + humidity_delta))
        if row.get("wind_speed") is not None:
            row["wind_speed"] = max(0, row["wind_speed"] + wind_delta)
        if row.get("precipitation") is not None:
            row["precipitation"] = max(0, row["precipitation"] + precip_delta)
    return data


__all__ = [
    "simulate_temperature_increase",
    "simulate_rainfall_change",
    "simulate_future_heat_scenario",
]
