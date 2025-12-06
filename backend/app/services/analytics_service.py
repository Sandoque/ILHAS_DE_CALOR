"""Analytics and aggregated insights services."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List

from sqlalchemy import and_, func

from ..extensions import db
from ..models import ClimateHourly, Station


def _parse_date(value: str | date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


def compute_statewide_heat_map(target_date: str | date | datetime) -> List[Dict[str, Any]]:
    """Return average apparent temperature per station for a given date."""
    day = _parse_date(target_date)
    if not day:
        return []
    results = (
        db.session.query(
            ClimateHourly.station_code,
            func.avg(ClimateHourly.apparent_temperature).label("avg_apparent_temp"),
            func.avg(ClimateHourly.heat_index).label("avg_heat_index"),
            Station.latitude,
            Station.longitude,
        )
        .join(Station, Station.station_code == ClimateHourly.station_code)
        .filter(func.date(ClimateHourly.datetime_utc) == day)
        .group_by(
            ClimateHourly.station_code,
            Station.latitude,
            Station.longitude,
        )
        .all()
    )
    return [dict(row._mapping) for row in results]


def compute_rank_hottest_stations(limit: int = 10) -> List[Dict[str, Any]]:
    """Rank stations by maximum apparent temperature."""
    results = (
        db.session.query(
            ClimateHourly.station_code,
            func.max(ClimateHourly.apparent_temperature).label("peak_apparent_temp"),
            func.max(ClimateHourly.temperature).label("peak_temp"),
        )
        .group_by(ClimateHourly.station_code)
        .order_by(func.max(ClimateHourly.apparent_temperature).desc())
        .limit(limit)
        .all()
    )
    return [dict(row._mapping) for row in results]


def compute_heat_alerts(threshold: float) -> List[Dict[str, Any]]:
    """Return records exceeding the given heat threshold."""
    results = (
        ClimateHourly.query.filter(
            and_(
                ClimateHourly.apparent_temperature.isnot(None),
                ClimateHourly.apparent_temperature >= threshold,
            )
        )
        .order_by(ClimateHourly.apparent_temperature.desc())
        .limit(500)
        .all()
    )
    from ..models import ClimateHourlySchema

    return ClimateHourlySchema(many=True).dump(results)


__all__ = [
    "compute_statewide_heat_map",
    "compute_rank_hottest_stations",
    "compute_heat_alerts",
]
