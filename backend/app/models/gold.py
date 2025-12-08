"""
SQLAlchemy models for GOLD climate metrics tables.
"""
from __future__ import annotations

from datetime import datetime

from app.extensions import db


class GoldClimaPeDiario(db.Model):
    """Daily aggregated climate metrics by city."""

    __tablename__ = "gold_clima_pe_diario"
    __table_args__ = (
        db.UniqueConstraint("id_cidade", "data", name="uq_gold_diario_cidade_data"),
    )

    id = db.Column(db.Integer, primary_key=True)
    id_cidade = db.Column(
        db.Integer,
        db.ForeignKey("dim_cidade_pe.id_cidade"),
        nullable=False,
    )
    data = db.Column(db.Date, nullable=False)

    temp_media = db.Column(db.Numeric(5, 2))
    temp_max = db.Column(db.Numeric(5, 2))
    temp_min = db.Column(db.Numeric(5, 2))
    umidade_media = db.Column(db.Numeric(5, 2))
    precipitacao_total = db.Column(db.Numeric(10, 2))
    radiacao_total = db.Column(db.Numeric(12, 2))
    amplitude_termica = db.Column(db.Numeric(5, 2))
    aparente_media = db.Column(db.Numeric(5, 2))
    heat_index_max = db.Column(db.Numeric(5, 2))
    rolling_heat_7d = db.Column(db.Numeric(5, 2))
    risco_calor = db.Column(db.String(20))

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "id_cidade": self.id_cidade,
            "data": self.data.isoformat() if self.data else None,
            "temp_media": float(self.temp_media) if self.temp_media else None,
            "temp_max": float(self.temp_max) if self.temp_max else None,
            "temp_min": float(self.temp_min) if self.temp_min else None,
            "umidade_media": float(self.umidade_media) if self.umidade_media else None,
            "precipitacao_total": float(self.precipitacao_total) if self.precipitacao_total else None,
            "radiacao_total": float(self.radiacao_total) if self.radiacao_total else None,
            "amplitude_termica": float(self.amplitude_termica) if self.amplitude_termica else None,
            "aparente_media": float(self.aparente_media) if self.aparente_media else None,
            "heat_index_max": float(self.heat_index_max) if self.heat_index_max else None,
            "rolling_heat_7d": float(self.rolling_heat_7d) if self.rolling_heat_7d else None,
            "risco_calor": self.risco_calor,
        }


__all__ = ["GoldClimaPeDiario"]
