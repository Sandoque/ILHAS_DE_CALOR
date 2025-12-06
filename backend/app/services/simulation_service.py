from typing import Dict


def run_mock_simulation(payload: Dict) -> Dict:
    """Return a mocked simulation result based on payload parameters."""
    aumento_vegetacao = float(payload.get("aumento_vegetacao", 0))
    reducao_area = float(payload.get("reducao_area_construida", 0))
    impacto_temp = round(0.3 * aumento_vegetacao + 0.1 * reducao_area, 2)
    return {
        "impacto_previsto_c": impacto_temp,
        "mensagem": f"Redução estimada de {impacto_temp}ºC na temperatura média",
    }
