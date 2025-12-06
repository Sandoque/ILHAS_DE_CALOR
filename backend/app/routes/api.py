from flask import Blueprint, jsonify, request
from ..services.simulation_service import run_mock_simulation
from ..services.climate_service import get_mock_state_overview, get_mock_city_series

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')


@api_bp.get('/cidades')
def list_cities():
    data = get_mock_state_overview()
    return jsonify(data['ranking'])


@api_bp.get('/cidade/<nome_cidade>/serie')
def city_series(nome_cidade: str):
    series = get_mock_city_series(nome_cidade)
    return jsonify(series)


@api_bp.post('/simulacao')
def simulate():
    payload = request.get_json(force=True) if request.data else {}
    result = run_mock_simulation(payload)
    return jsonify(result)
