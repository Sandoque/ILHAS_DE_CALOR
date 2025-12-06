"""Shared Flask extensions."""
from __future__ import annotations

from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions (bound in create_app)
db = SQLAlchemy()
ma = Marshmallow()
cors = CORS()


__all__ = ["db", "ma", "cors"]
