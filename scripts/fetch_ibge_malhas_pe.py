#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para baixar malhas geográficas dos municípios de Pernambuco
usando a API v4 do IBGE e consolidar em um único FeatureCollection.

Uso:
    python scripts/fetch_ibge_malhas_pe.py
"""

import json
import logging
import time
from pathlib import Path

import requests

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constantes de API
IBGE_MUNICIPIOS_PE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/26/municipios"
IBGE_MALHA_MUNICIPIO_URL = "https://servicodados.ibge.gov.br/api/v4/malhas/municipios/{id}?formato=application/vnd.geo+json"
IBGE_MALHA_ESTADO_PE = "https://servicodados.ibge.gov.br/api/v4/malhas/estados/26?formato=application/vnd.geo+json"

# Caminhos de saída
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "backend" / "app" / "static" / "geo"
OUTPUT_MUNICIPIOS = OUTPUT_DIR / "municipios_pe.geojson"
OUTPUT_ESTADO = OUTPUT_DIR / "estado_pe.geojson"

# Configurações de requisição
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 1  # segundos


def fetch_with_retry(url: str, timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES) -> dict:
    """
    Faz requisição HTTP com retry automático.
    
    Args:
        url: URL para requisição
        timeout: Timeout em segundos
        max_retries: Número máximo de tentativas
        
    Returns:
        Resposta JSON parseada
        
    Raises:
        requests.RequestException: Se falhar após todas as retries
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Tentativa {attempt}/{max_retries}: {url}")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries:
                logger.error(f"Falha após {max_retries} tentativas: {e}")
                raise
            logger.warning(f"Tentativa {attempt} falhou: {e}. Aguardando {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)


def fetch_municipios_pe() -> list:
    """
    Busca lista de municípios de Pernambuco (UF 26).
    
    Returns:
        Lista de dicts com 'id' e 'nome' de cada município
    """
    logger.info("Buscando lista de municípios de PE...")
    municipios = fetch_with_retry(IBGE_MUNICIPIOS_PE_URL)
    logger.info(f"Encontrados {len(municipios)} municípios em PE")
    return municipios


def fetch_malha_municipio(municipio_id: int, municipio_nome: str) -> dict | None:
    """
    Baixa a malha GeoJSON de um município específico.
    
    Args:
        municipio_id: ID IBGE do município
        municipio_nome: Nome do município (para logging)
        
    Returns:
        Feature ou FeatureCollection com as geometrias, ou None se falhar
    """
    url = IBGE_MALHA_MUNICIPIO_URL.format(id=municipio_id)
    
    try:
        logger.info(f"Buscando malha: {municipio_nome} (ID: {municipio_id})")
        data = fetch_with_retry(url, max_retries=2)  # Retry menos agressivo para municípios
        return data
    except Exception as e:
        logger.error(f"Erro ao buscar malha de {municipio_nome}: {e}")
        return None


def normalize_feature(feature: dict, municipio_id: int, municipio_nome: str) -> dict:
    """
    Normaliza uma feature para garantir que tenha properties consistentes.
    
    Args:
        feature: Feature GeoJSON
        municipio_id: ID IBGE do município
        municipio_nome: Nome do município
        
    Returns:
        Feature normalizado
    """
    if feature["type"] != "Feature":
        logger.warning(f"Feature não é do tipo 'Feature': {feature.get('type')}")
        return None
    
    # Garantir que properties existe e tem os campos esperados
    if not feature.get("properties"):
        feature["properties"] = {}
    
    # Adicionar/manter ID e nome do município
    # Usar múltiplos nomes para máxima compatibilidade com diferentes consumidores
    feature["properties"]["id"] = municipio_id              # Para Leaflet/mapa.html
    feature["properties"]["codigo"] = municipio_id          # Fallback Leaflet
    feature["properties"]["codarea"] = municipio_id         # Para referência IBGE
    feature["properties"]["nome"] = municipio_nome
    
    return feature


def consolidate_malhas(municipios: list) -> list:
    """
    Consolida malhas de todos os municípios em uma lista de features.
    
    Args:
        municipios: Lista de dicts com 'id' e 'nome'
        
    Returns:
        Lista de features normalizadas
    """
    features = []
    
    for idx, municipio in enumerate(municipios, 1):
        municipio_id = municipio["id"]
        municipio_nome = municipio["nome"]
        
        logger.info(f"[{idx}/{len(municipios)}] Processando {municipio_nome}...")
        
        # Buscar malha
        malha_data = fetch_malha_municipio(municipio_id, municipio_nome)
        if not malha_data:
            logger.warning(f"Pulando {municipio_nome} (erro ao buscar)")
            continue
        
        # Se retornou FeatureCollection, extrair features
        if malha_data.get("type") == "FeatureCollection":
            collection_features = malha_data.get("features", [])
            for feature in collection_features:
                normalized = normalize_feature(feature, municipio_id, municipio_nome)
                if normalized:
                    features.append(normalized)
        # Se retornou Feature única
        elif malha_data.get("type") == "Feature":
            normalized = normalize_feature(malha_data, municipio_id, municipio_nome)
            if normalized:
                features.append(normalized)
        else:
            logger.warning(f"Formato inesperado para {municipio_nome}: {malha_data.get('type')}")
    
    logger.info(f"Total de features consolidadas: {len(features)}")
    return features


def save_geojson(features: list, output_path: Path) -> None:
    """
    Salva features consolidadas em um FeatureCollection GeoJSON.
    
    Args:
        features: Lista de features
        output_path: Caminho do arquivo de saída
    """
    feature_collection = {
        "type": "FeatureCollection",
        "features": features,
    }
    
    # Criar diretório se não existir
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Salvar com encoding UTF-8 e sem escape ASCII
    try:
        output_path.write_text(
            json.dumps(feature_collection, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"✅ GeoJSON salvo com sucesso: {output_path}")
        logger.info(f"   - Total de features: {len(features)}")
        logger.info(f"   - Tamanho: {output_path.stat().st_size / 1024:.2f} KB")
    except Exception as e:
        logger.error(f"Erro ao salvar GeoJSON: {e}")
        raise


def fetch_estado_pe() -> None:
    """
    Baixa e salva a malha do estado de PE (para uso futuro).
    """
    logger.info("Buscando malha do estado de PE...")
    
    try:
        malha_estado = fetch_with_retry(IBGE_MALHA_ESTADO_PE, max_retries=2)
        
        if malha_estado.get("type") == "FeatureCollection":
            # Se é uma FeatureCollection, envolver em outra para manter consistência
            feature_collection = malha_estado
        else:
            # Envolver em FeatureCollection
            feature_collection = {
                "type": "FeatureCollection",
                "features": [malha_estado] if malha_estado.get("type") == "Feature" else [],
            }
        
        # Salvar
        OUTPUT_ESTADO.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_ESTADO.write_text(
            json.dumps(feature_collection, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"✅ Malha do estado PE salva: {OUTPUT_ESTADO}")
        logger.info(f"   - Tamanho: {OUTPUT_ESTADO.stat().st_size / 1024:.2f} KB")
    except Exception as e:
        logger.error(f"Erro ao buscar malha do estado: {e}")
        logger.info("Continuando com malhas dos municípios...")


def main():
    """Função principal."""
    logger.info("=" * 70)
    logger.info("INICIANDO DOWNLOAD DE MALHAS GEOGRÁFICAS DE PE (IBGE v4)")
    logger.info("=" * 70)
    
    try:
        # 1. Buscar lista de municípios
        municipios = fetch_municipios_pe()
        
        # 2. Consolidar malhas dos municípios
        features = consolidate_malhas(municipios)
        
        if not features:
            logger.error("Nenhuma feature foi consolidada!")
            return False
        
        # 3. Salvar GeoJSON consolidado
        save_geojson(features, OUTPUT_MUNICIPIOS)
        
        # 4. (Opcional) Buscar e salvar malha do estado
        logger.info("-" * 70)
        fetch_estado_pe()
        
        logger.info("=" * 70)
        logger.info("✅ PROCESSO CONCLUÍDO COM SUCESSO!")
        logger.info("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
