"""Web pages for basic views."""
from __future__ import annotations

from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/city/<code>")
def city_detail(code: str):
    return render_template("city_detail.html", station_code=code)


@bp.route("/simulator")
def simulator():
    return render_template("simulator.html")
