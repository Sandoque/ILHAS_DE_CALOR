"""Station metadata model."""
from __future__ import annotations

from ..extensions import db, ma


class Station(db.Model):
    __tablename__ = "stations"

    station_code = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(120))
    uf = db.Column(db.String(2), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    altitude = db.Column(db.Float)
    municipality = db.Column(db.String(120))

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Station {self.station_code}>"


class StationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Station
        load_instance = True
        ordered = True


__all__ = ["Station", "StationSchema"]
