"""Station-related business logic."""
from __future__ import annotations

from typing import List, Optional

from ..extensions import db
from ..models import Station, StationSchema

station_schema_many = StationSchema(many=True)
station_schema = StationSchema()


def list_stations() -> List[dict]:
    stations = Station.query.order_by(Station.station_code).all()
    return station_schema_many.dump(stations)


def get_station_details(station_code: str) -> Optional[dict]:
    station = Station.query.filter_by(station_code=station_code).first()
    if not station:
        return None
    return station_schema.dump(station)


__all__ = ["list_stations", "get_station_details"]
