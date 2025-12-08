"""
Flask API endpoints for GOLD climate metrics.

Routes:
    GET /api/gold/<cidade_id>/diario    - Last 7 days + current day
    GET /api/gold/<cidade_id>/risco     - Current heat risk
    GET /api/gold/<cidade_id>/serie     - Full daily time series
"""
from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from app.models.gold import GoldClimaPeDiario
from app.utils.responses import success, error

api_gold = Blueprint("api_gold", __name__, url_prefix="/api/gold")


@api_gold.route("/<int:cidade_id>/diario", methods=["GET"])
def get_last_days(cidade_id: int):
    """
    Get last 7 days + current day of daily climate metrics.
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "data": "2025-12-07",
                    "temp_media": 28.5,
                    "temp_max": 32.1,
                    "temp_min": 24.3,
                    ...
                    "risco_calor": "Alto"
                },
                ...
            ]
        }
    """
    try:
        # Get last 8 days (7 previous + today)
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=7)
        
        records = (
            GoldClimaPeDiario.query.filter(
                GoldClimaPeDiario.id_cidade == cidade_id,
                GoldClimaPeDiario.data >= start_date,
            )
            .order_by(GoldClimaPeDiario.data.desc())
            .all()
        )
        
        if not records:
            return success([])
        
        data = [record.to_dict() for record in records]
        return success(data)
    
    except Exception as e:
        return error(f"Failed to retrieve daily metrics: {str(e)}", status=500)


@api_gold.route("/<int:cidade_id>/risco", methods=["GET"])
def get_current_risk(cidade_id: int):
    """
    Get current (latest) heat risk classification.
    
    Returns:
        {
            "success": true,
            "data": {
                "data": "2025-12-07",
                "risco_calor": "Alto",
                "heat_index_max": 38.5,
                "temp_max": 32.1
            }
        }
    """
    try:
        record = (
            GoldClimaPeDiario.query.filter(
                GoldClimaPeDiario.id_cidade == cidade_id,
            )
            .order_by(GoldClimaPeDiario.data.desc())
            .first()
        )
        
        if not record:
            return error("No risk data found for this city", status=404)
        
        data = {
            "data": record.data.isoformat() if record.data else None,
            "risco_calor": record.risco_calor,
            "heat_index_max": float(record.heat_index_max) if record.heat_index_max else None,
            "temp_max": float(record.temp_max) if record.temp_max else None,
            "temp_media": float(record.temp_media) if record.temp_media else None,
            "umidade_media": float(record.umidade_media) if record.umidade_media else None,
        }
        
        return success(data)
    
    except Exception as e:
        return error(f"Failed to retrieve risk data: {str(e)}", status=500)


@api_gold.route("/<int:cidade_id>/serie", methods=["GET"])
def get_time_series(cidade_id: int):
    """
    Get full daily time series of climate metrics.
    
    Query parameters:
        start_date: YYYY-MM-DD (optional)
        end_date: YYYY-MM-DD (optional)
        limit: max records to return (default: 365)
    
    Returns:
        {
            "success": true,
            "data": [
                { "data": "2025-01-01", ... },
                ...
            ],
            "total": 365
        }
    """
    try:
        # Parse query parameters
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        limit = request.args.get("limit", default=365, type=int)
        
        query = GoldClimaPeDiario.query.filter(GoldClimaPeDiario.id_cidade == cidade_id)
        
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(GoldClimaPeDiario.data >= start_date)
            except ValueError:
                return error("Invalid start_date format. Use YYYY-MM-DD", status=400)
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(GoldClimaPeDiario.data <= end_date)
            except ValueError:
                return error("Invalid end_date format. Use YYYY-MM-DD", status=400)
        
        # Order by date and limit
        records = (
            query.order_by(GoldClimaPeDiario.data.asc())
            .limit(limit)
            .all()
        )
        
        if not records:
            return success({"data": [], "total": 0})
        
        data = [record.to_dict() for record in records]
        
        return success({"data": data, "total": len(data)})
    
    except Exception as e:
        return error(f"Failed to retrieve time series: {str(e)}", status=500)


__all__ = ["api_gold"]
