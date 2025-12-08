# -*- coding: utf-8 -*-
"""
API routes para servir dados geográficos em GeoJSON.

Endpoints:
  - GET /api/geo/municipios-pe: Retorna GeoJSON com todos os municípios de PE
  - GET /api/geo/estado-pe: Retorna GeoJSON com a geometria do estado de PE
"""

from pathlib import Path

from flask import Blueprint, jsonify, send_from_directory, current_app
import json

api_geo_bp = Blueprint('api_geo', __name__, url_prefix='/api/geo')

# Caminhos aos arquivos GeoJSON estáticos
GEO_DIR = Path(__file__).parent.parent / 'static' / 'geo'
MUNICIPIOS_PE_FILE = GEO_DIR / 'municipios_pe.geojson'
ESTADO_PE_FILE = GEO_DIR / 'estado_pe.geojson'


@api_geo_bp.route('/municipios-pe', methods=['GET'])
def get_municipios_pe():
    """
    Retorna GeoJSON com todos os municípios de Pernambuco.
    
    Returns:
        JSON (GeoJSON FeatureCollection) com as geometrias de todos os municípios
        
    Status Codes:
        200: Sucesso
        404: Arquivo não encontrado (execute `python scripts/fetch_ibge_malhas_pe.py`)
        500: Erro ao ler arquivo
    """
    try:
        if not MUNICIPIOS_PE_FILE.exists():
            return jsonify({
                'success': False,
                'error': 'Arquivo de municípios PE não encontrado. Execute: python scripts/fetch_ibge_malhas_pe.py'
            }), 404
        
        # Ler e retornar o arquivo GeoJSON
        with open(MUNICIPIOS_PE_FILE, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # Registrar no log (opcional)
        current_app.logger.info(
            f"Servindo GeoJSON de municípios PE: {len(geojson_data.get('features', []))} features"
        )
        
        return jsonify(geojson_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao servir GeoJSON de municípios: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao processar arquivo: {str(e)}'
        }), 500


@api_geo_bp.route('/estado-pe', methods=['GET'])
def get_estado_pe():
    """
    Retorna GeoJSON com a geometria do estado de Pernambuco.
    
    Returns:
        JSON (GeoJSON FeatureCollection) com a geometria do estado
        
    Status Codes:
        200: Sucesso
        404: Arquivo não encontrado (execute `python scripts/fetch_ibge_malhas_pe.py`)
        500: Erro ao ler arquivo
    """
    try:
        if not ESTADO_PE_FILE.exists():
            return jsonify({
                'success': False,
                'error': 'Arquivo de estado PE não encontrado. Execute: python scripts/fetch_ibge_malhas_pe.py'
            }), 404
        
        # Ler e retornar o arquivo GeoJSON
        with open(ESTADO_PE_FILE, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        
        # Registrar no log (opcional)
        current_app.logger.info(
            f"Servindo GeoJSON do estado PE: {len(geojson_data.get('features', []))} features"
        )
        
        return jsonify(geojson_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Erro ao servir GeoJSON do estado: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao processar arquivo: {str(e)}'
        }), 500


@api_geo_bp.route('/municipios-pe/raw', methods=['GET'])
def get_municipios_pe_raw():
    """
    Retorna o arquivo GeoJSON bruto (raw) com content-type correto.
    
    Returns:
        File response com MIME type: application/geo+json
    """
    try:
        if not MUNICIPIOS_PE_FILE.exists():
            return jsonify({
                'success': False,
                'error': 'Arquivo de municípios PE não encontrado'
            }), 404
        
        # Enviar arquivo com MIME type correto para GeoJSON
        return send_from_directory(
            GEO_DIR,
            'municipios_pe.geojson',
            mimetype='application/geo+json'
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro ao servir GeoJSON bruto: {e}")
        return jsonify({
            'success': False,
            'error': f'Erro ao servir arquivo: {str(e)}'
        }), 500
