"""Blueprint registration for API and web routes."""
from __future__ import annotations

from flask import Flask


def register_blueprints(app: Flask) -> None:
    from .api_climate import bp as climate_bp
    from .api_stations import bp as stations_bp
    from .api_simulation import bp as simulation_bp
    from .api_analytics import bp as analytics_bp
    from .main import bp as main_bp

    app.register_blueprint(climate_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(main_bp)


__all__ = ["register_blueprints"]
