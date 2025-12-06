"""Daily metrics materialized view model."""
from __future__ import annotations

from datetime import date

from ..extensions import db, ma


class DailyMetrics(db.Model):
    __tablename__ = "daily_metrics"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    station_code = db.Column(db.String(10), nullable=False, index=True)
    max_temp = db.Column(db.Float)
    min_temp = db.Column(db.Float)
    avg_temp = db.Column(db.Float)
    heat_index_max = db.Column(db.Float)
    thermal_amplitude = db.Column(db.Float)
    precipitation_total = db.Column(db.Float)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<DailyMetrics {self.station_code} {self.date}>"


class DailyMetricsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DailyMetrics
        load_instance = True
        ordered = True


__all__ = ["DailyMetrics", "DailyMetricsSchema"]
