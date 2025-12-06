from flask import Flask
from .config import Config
from .extensions import db
from .routes.main import main_bp
from .routes.api import api_bp


def create_app() -> Flask:
    """Application factory for the Observatorio Estadual de Ilhas de Calor - PE."""
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    return app
