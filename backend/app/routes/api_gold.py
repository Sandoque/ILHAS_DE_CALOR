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


@api_gold.route("/cidades", methods=["GET"])
def list_cities():
    """
    Get list of all cities with GOLD climate data.
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "id_cidade": 1,
                    "nome_cidade": "Recife",
                    "uf": "PE",
                    "codigo_ibge": "2611606"
                },
                ...
            ]
        }
    """
    try:
        # Query distinct cidades from GOLD table
        from sqlalchemy import distinct
        
        cidade_ids = (
            GoldClimaPeDiario.query
            .distinct(GoldClimaPeDiario.id_cidade)
            .with_entities(
                GoldClimaPeDiario.id_cidade,
                GoldClimaPeDiario.nome_cidade,
                GoldClimaPeDiario.uf,
                GoldClimaPeDiario.codigo_ibge
            )
            .order_by(GoldClimaPeDiario.nome_cidade)
            .all()
        )
        
        if not cidade_ids:
            return success([])
        
        data = [
            {
                "id_cidade": row[0],
                "nome_cidade": row[1],
                "uf": row[2],
                "codigo_ibge": row[3]
            }
            for row in cidade_ids
        ]
        
        return success(data)
    
    except Exception as e:
        return error(f"Failed to retrieve cities: {str(e)}", status=500)


@api_gold.route("/<int:cidade_id>/resumo", methods=["GET"])
def get_city_summary(cidade_id: int):
    """
    Get summary metrics for a city (latest day + 7-day trend).
    
    Returns:
        {
            "success": true,
            "data": {
                "id_cidade": 1,
                "nome_cidade": "Recife",
                "data_atual": "2025-12-07",
                "risco_calor": "Alto",
                "heat_index_max": 35.2,
                "temp_max": 32.1,
                "temp_media": 28.5,
                "temp_min": 24.3,
                "umidade_media": 65.3,
                "dias_risco_alto_7d": 4,
                "tendencia_temp": "aumentando"
            }
        }
    """
    try:
        # Get today's data
        today = datetime.utcnow().date()
        today_record = (
            GoldClimaPeDiario.query.filter(
                GoldClimaPeDiario.id_cidade == cidade_id,
                GoldClimaPeDiario.data == today
            )
            .first()
        )
        
        if not today_record:
            # Fallback to latest available date
            today_record = (
                GoldClimaPeDiario.query.filter(
                    GoldClimaPeDiario.id_cidade == cidade_id
                )
                .order_by(GoldClimaPeDiario.data.desc())
                .first()
            )
        
        if not today_record:
            return error(f"No data found for city {cidade_id}", status=404)
        
        # Get last 7 days for trend analysis
        start_date = today_record.data - timedelta(days=7)
        last_7_days = (
            GoldClimaPeDiario.query.filter(
                GoldClimaPeDiario.id_cidade == cidade_id,
                GoldClimaPeDiario.data >= start_date,
                GoldClimaPeDiario.data <= today_record.data
            )
            .order_by(GoldClimaPeDiario.data.asc())
            .all()
        )
        
        # Calculate 7-day statistics
        dias_risco_alto_7d = sum(
            1 for r in last_7_days 
            if r.risco_calor in ["Alto", "Muito Alto", "Extremo"]
        )
        
        # Calculate temperature trend (compare first 3 days vs last 3 days)
        if len(last_7_days) >= 6:
            temp_media_first_3 = sum(r.temp_media or 0 for r in last_7_days[:3]) / 3
            temp_media_last_3 = sum(r.temp_media or 0 for r in last_7_days[-3:]) / 3
            tendencia = "aumentando" if temp_media_last_3 > temp_media_first_3 else "diminuindo"
        else:
            tendencia = "estável"
        
        data = {
            "id_cidade": today_record.id_cidade,
            "nome_cidade": today_record.nome_cidade,
            "uf": today_record.uf,
            "codigo_ibge": today_record.codigo_ibge,
            "data_atual": today_record.data.isoformat(),
            "risco_calor": today_record.risco_calor,
            "heat_index_max": today_record.heat_index_max,
            "temp_max": today_record.temp_max,
            "temp_media": today_record.temp_media,
            "temp_min": today_record.temp_min,
            "umidade_media": today_record.umidade_media,
            "dias_risco_alto_7d": dias_risco_alto_7d,
            "tendencia_temp": tendencia
        }
        
        return success(data)
    
    except Exception as e:
        return error(f"Failed to retrieve city summary: {str(e)}", status=500)


__all__ = ["api_gold"]
