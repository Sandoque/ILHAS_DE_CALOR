"""Dashboard routes for interactive data visualization."""
from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify
import logging

from app.models import GoldClimaPeDiario
from app.extensions import db
from app.utils.responses import success, error

logger = logging.getLogger(__name__)

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
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering dashboard index: {str(e)}")
        return error("Failed to load dashboard", status=500)


@dashboard_bp.route("/cidade/<int:cidade_id>", methods=["GET"])
def view_city(cidade_id: int):
    """City dashboard with charts and metrics.
    
    Args:
        cidade_id: City ID from database
        range (query param): Days to display (7, 30, 90, 365)
    
    Returns:
        - If HX-Request header: Returns partial HTML (cidade_charts.html)
        - Else: Returns full page (cidade.html with sidebar/header)
    """
    try:
        # Parse range parameter
        range_str = request.args.get("range", default="30", type=str)
        try:
            days = int(range_str)
            if days not in [7, 30, 90, 365]:
                days = 30
        except (ValueError, TypeError):
            days = 30
        
        # Detect HTMX request (partial reload)
        is_htmx = request.headers.get("HX-Request", "false").lower() == "true"
        
        logger.debug(f"City view: id={cidade_id}, range={days}, htmx={is_htmx}")
        
        # Verify cidade_id exists in database
        cidade_exists = db.session.query(
            db.exists().where(GoldClimaPeDiario.id_cidade == cidade_id)
        ).scalar()
        
        if not cidade_exists:
            logger.warning(f"Cidade {cidade_id} not found in database")
            return error(f"Cidade {cidade_id} não encontrada", status=404)
        
        # Return appropriate response based on HTMX detection
        if is_htmx:
            # Partial response for HTMX swaps
            return render_template(
                "cidade_charts.html",
                cidade_id=cidade_id,
                range=days
            ), 200, {"HX-Trigger-After-Swap": "chartsLoaded"}
        else:
            # Full page response
            return render_template(
                "cidade.html",
                cidade_id=cidade_id,
                range=days
            )
    
    except Exception as e:
        logger.exception(f"Error in city view: {str(e)}")
        return error(f"Erro ao carregar dashboard da cidade: {str(e)}", status=500)


@dashboard_bp.route("/compare", methods=["GET"])
def compare():
    """Comparison page for multiple cities."""
    return render_template("compare.html")


__all__ = ["dashboard_bp"]
