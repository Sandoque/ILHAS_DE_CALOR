from flask import Blueprint, render_template
from ..services.climate_service import get_mock_state_overview, get_mock_city_detail

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def index():
    overview = get_mock_state_overview()
    return render_template('index.html', overview=overview)


@main_bp.route('/cidade/<nome_cidade>')
def city_detail(nome_cidade: str):
    city_data = get_mock_city_detail(nome_cidade)
    return render_template('city_detail.html', city=city_data)


@main_bp.route('/simulador/<nome_cidade>')
def simulator(nome_cidade: str):
    city_data = get_mock_city_detail(nome_cidade)
    return render_template('simulator.html', city=city_data)
