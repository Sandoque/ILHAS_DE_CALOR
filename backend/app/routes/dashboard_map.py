"""
Map routes for interactive geographic visualization of heat risk.

Routes:
    GET /dashboard/mapa           - Main map page
    GET /dashboard/mapa/dados     - API endpoint with risk data by municipality
"""
from __future__ import annotations

from flask import Blueprint, render_template
import logging

from app.models import GoldClimaPeDiario
from app.extensions import db
from app.utils.responses import success, error

logger = logging.getLogger(__name__)

map_bp = Blueprint(
    "map",
    __name__,
    url_prefix="/dashboard/mapa",
    template_folder="../templates",
    static_folder="../static",
)


@map_bp.route("/", methods=["GET"])
def map_main():
    """Main map page - displays Pernambuco municipalities with heat risk colors.
    
    Returns:
        Rendered HTML template: mapa.html
    """
    try:
        return render_template("mapa.html")
    except Exception as e:
        logger.error(f"Error rendering map page: {str(e)}")
        return error("Failed to load map", status=500)


@map_bp.route("/dados", methods=["GET"])
def map_risk_data():
    """API endpoint returning heat risk data by municipality.
    
    Returns JSON with municipality data:
    {
        "success": true,
        "data": [
            {
                "id_cidade": 1,
                "nome_cidade": "Recife",
                "indice_risco": 72,
                "categoria": "Alto",
                "lat": -8.05,
                "lon": -34.9
            },
            ...
        ]
    }
    """
    try:
        # Query latest risk data by municipality
        from sqlalchemy import func, desc
        
        # Get latest month data for each city
        latest_risk = (
            db.session.query(
                GoldClimaPeDiario.id_cidade,
                GoldClimaPeDiario.nome_cidade,
                GoldClimaPeDiario.uf,
                GoldClimaPeDiario.risco_calor,
                func.avg(GoldClimaPeDiario.heat_index_max).label('heat_index_avg'),
                func.row_number().over(
                    partition_by=GoldClimaPeDiario.id_cidade,
                    order_by=desc(GoldClimaPeDiario.data)
                ).label('rn')
            )
            .filter(GoldClimaPeDiario.uf == 'PE')
            .all()
        )
        
        if not latest_risk:
            logger.warning("No risk data found in database")
            return success([])
        
        # Build response with risco score (0-100) based on heat_index_avg
        municipios = []
        seen_ids = set()
        
        for record in latest_risk:
            if record.id_cidade in seen_ids:
                continue
            seen_ids.add(record.id_cidade)
            
            # Map risco_calor category to risk score (0-100)
            risk_scores = {
                'Baixo': 20,
                'Moderado': 40,
                'Alto': 60,
                'Muito Alto': 80,
                'Extremo': 100
            }
            risco_score = risk_scores.get(record.risco_calor, 50)
            
            municipios.append({
                'id_cidade': record.id_cidade,
                'nome_cidade': record.nome_cidade,
                'uf': record.uf,
                'risco': risco_score,
                'categoria': record.risco_calor,
                'heat_index_avg': round(float(record.heat_index_avg) if record.heat_index_avg else 0, 1)
            })
        
        logger.info(f"Retrieved risk data for {len(municipios)} municipalities")
        return success(municipios)
    
    except Exception as e:
        logger.exception(f"Error retrieving map risk data: {str(e)}")
        return error(f"Failed to retrieve risk data: {str(e)}", status=500)


__all__ = ["map_bp"]
