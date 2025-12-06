from datetime import datetime, timedelta
from typing import Dict, List


CITIES = [
    {"nome": "Recife", "risco": 0.82},
    {"nome": "Olinda", "risco": 0.74},
    {"nome": "Caruaru", "risco": 0.63},
    {"nome": "Petrolina", "risco": 0.71},
    {"nome": "Garanhuns", "risco": 0.52},
]


def get_mock_state_overview() -> Dict:
    """Return mocked overview data for the state ranking and highlights."""
    return {
        "resumo": {
            "temp_media": 29.3,
            "alertas_calor": 12,
            "estacoes_monitoradas": 35,
        },
        "ranking": CITIES,
    }


def get_mock_city_detail(nome_cidade: str) -> Dict:
    """Return mocked detail data for a given city."""
    base = next((c for c in CITIES if c["nome"].lower() == nome_cidade.lower()), None)
    base_name = base["nome"] if base else nome_cidade
    return {
        "nome": base_name,
        "temp_media": 28.7,
        "umidade_media": 68,
        "pontos_quentes": 5,
        "series": get_mock_city_series(base_name),
        "insights": [
            "Areas centrais apresentam maior retencao de calor",
            "Aumento de vegetacao pode reduzir picos em ate 1.2C",
            "Periodo noturno mantem temperatura elevada em zonas urbanizadas",
        ],
    }


def get_mock_city_series(nome_cidade: str) -> List[Dict]:
    """Return mocked time series for a city."""
    now = datetime.utcnow()
    series = []
    for i in range(7):
        point_time = now - timedelta(days=6 - i)
        series.append({
            "data": point_time.strftime("%Y-%m-%d"),
            "temp": 26 + i * 0.5,
        })
    return {"cidade": nome_cidade, "serie": series}
