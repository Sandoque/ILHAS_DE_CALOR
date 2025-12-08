"""Dashboard routes for interactive data visualization."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify

from app.models import GoldClimaPeDiario
from app.extensions import db
from app.utils.responses import success, error

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
    template_folder="../templates/dashboard",
    static_folder="../static",
)


@dashboard_bp.route("/", methods=["GET"])
def index():
    """Main dashboard page with city selector."""
    return render_template("index.html")


@dashboard_bp.route("/cidade/<int:cidade_id>", methods=["GET"])
def view_city(cidade_id: int):
    """City dashboard with charts and metrics."""
    range_days = request.args.get("range", default="30", type=str)
    
    try:
        # Validate range parameter
        try:
            days = int(range_days)
            if days not in [7, 30, 90, 365]:
                days = 30
        except (ValueError, TypeError):
            days = 30
        
        # For HTMX requests, return only the charts partial
        if request.headers.get("HX-Request"):
            return render_template("cidade_charts.html", cidade_id=cidade_id, range=days)
        
        # Full page load
        return render_template("cidade.html", cidade_id=cidade_id, range=days)
    
    except Exception as e:
        return error(f"Failed to load city dashboard: {str(e)}", status=500)


@dashboard_bp.route("/compare", methods=["GET"])
def compare():
    """Comparison page for multiple cities."""
    return render_template("compare.html")


__all__ = ["dashboard_bp"]
