"""Flask application factory for Observatorio Estadual de Ilhas de Calor – PE."""
from __future__ import annotations

from flask import Flask

from .config import get_config
from .extensions import cors, db, ma
from .routes import register_blueprints


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config())

    # Initialize extensions
    cors.init_app(app)
    db.init_app(app)
    ma.init_app(app)

    # Register blueprints
    register_blueprints(app)

    return app


__all__ = ["create_app"]
