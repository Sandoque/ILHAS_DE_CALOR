"""Business logic for climate data access."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func

from ..extensions import db
from ..models import ClimateHourly, ClimateHourlySchema

schema_many = ClimateHourlySchema(many=True)


def _parse_datetime(value: str | datetime | None) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def get_climate_by_station(station_code: str, start: str | datetime | None, end: str | datetime | None) -> List[dict]:
    """Return climate rows for a station between optional start/end datetimes."""
    query = ClimateHourly.query.filter(ClimateHourly.station_code == station_code)
    start_dt = _parse_datetime(start)
    end_dt = _parse_datetime(end)
    if start_dt:
        query = query.filter(ClimateHourly.datetime_utc >= start_dt)
    if end_dt:
        query = query.filter(ClimateHourly.datetime_utc <= end_dt)
    results = query.order_by(ClimateHourly.datetime_utc.desc()).limit(5000).all()
    return schema_many.dump(results)


def get_daily_summary(station_code: str, limit: int = 30) -> List[Dict[str, Any]]:
    """Aggregate daily metrics for a station."""
    aggregation = (
        db.session.query(
            func.date(ClimateHourly.datetime_utc).label("date"),
            func.max(ClimateHourly.temperature).label("max_temp"),
            func.min(ClimateHourly.temperature).label("min_temp"),
            func.avg(ClimateHourly.temperature).label("avg_temp"),
            func.max(ClimateHourly.heat_index).label("heat_index_max"),
            func.max(ClimateHourly.thermal_amplitude).label("thermal_amplitude"),
            func.sum(ClimateHourly.precipitation).label("precipitation_total"),
        )
        .filter(ClimateHourly.station_code == station_code)
        .group_by(func.date(ClimateHourly.datetime_utc))
        .order_by(func.date(ClimateHourly.datetime_utc).desc())
        .limit(limit)
    )
    rows = aggregation.all()
    return [dict(row._mapping) for row in rows]


def list_years_available() -> List[int]:
    """List distinct years available in the climate table."""
    years = (
        db.session.query(func.extract("year", ClimateHourly.datetime_utc))
        .distinct()
        .order_by(func.extract("year", ClimateHourly.datetime_utc))
        .all()
    )
    return [int(y[0]) for y in years if y[0] is not None]


def compute_trends(station_code: str) -> Dict[str, Any]:
    """Compute basic trend metrics for a station."""
    stats = (
        db.session.query(
            func.avg(ClimateHourly.temperature).label("avg_temp"),
            func.max(ClimateHourly.temperature).label("max_temp"),
            func.min(ClimateHourly.temperature).label("min_temp"),
            func.avg(ClimateHourly.humidity).label("avg_humidity"),
            func.avg(ClimateHourly.wind_speed).label("avg_wind_speed"),
        )
        .filter(ClimateHourly.station_code == station_code)
        .one_or_none()
    )
    if not stats:
        return {}
    mapping = stats._mapping
    return {
        "avg_temp": mapping.get("avg_temp"),
        "max_temp": mapping.get("max_temp"),
        "min_temp": mapping.get("min_temp"),
        "avg_humidity": mapping.get("avg_humidity"),
        "avg_wind_speed": mapping.get("avg_wind_speed"),
    }


__all__ = [
    "get_climate_by_station",
    "get_daily_summary",
    "list_years_available",
    "compute_trends",
]
