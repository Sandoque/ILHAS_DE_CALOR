"""Climate hourly model and schema."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Index

from ..extensions import db, ma


class ClimateHourly(db.Model):
    __tablename__ = "climate_hourly"

    id = db.Column(db.Integer, primary_key=True)
    datetime_utc = db.Column(db.DateTime, nullable=False, index=True)
    station_code = db.Column(db.String(10), nullable=False, index=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    radiation = db.Column(db.Float)
    precipitation = db.Column(db.Float)
    apparent_temperature = db.Column(db.Float)
    heat_index = db.Column(db.Float)
    thermal_amplitude = db.Column(db.Float)
    rolling_heat_7d = db.Column(db.Float)

    __table_args__ = (Index("ix_climate_station_date", "station_code", "datetime_utc"),)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ClimateHourly {self.station_code} {self.datetime_utc}>"


class ClimateHourlySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClimateHourly
        load_instance = True
        include_fk = True
        ordered = True


__all__ = ["ClimateHourly", "ClimateHourlySchema"]
