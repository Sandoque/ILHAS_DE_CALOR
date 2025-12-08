#!/usr/bin/env python3
"""
Download GeoJSON data for Pernambuco municipalities from IBGE API.
"""
import requests
import json
import sys
from pathlib import Path

def download_geojson():
    """Download and save GeoJSON from IBGE API."""
    # IBGE API para GeoJSON de Pernambuco (estado)
    url = 'https://servicodados.ibge.gov.br/api/v1/malhas/estados/26'
    output_path = Path('backend/app/static/geo/municipios_pe.geojson')
    
    print('Baixando GeoJSON de Pernambuco via IBGE API...')
    print(f'URL: {url}')
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f'Erro: HTTP {response.status_code}')
            return False
        
        geojson = response.json()
        features = len(geojson.get('features', []))
        
        # Create directory if not exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save with UTF-8 encoding
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        
        print(f'✓ GeoJSON salvo com sucesso!')
        print(f'  Arquivo: {output_path}')
        print(f'  Municípios: {features}')
        print(f'  Encoding: UTF-8')
        return True
    
    except requests.RequestException as e:
        print(f'✗ Erro na requisição: {e}')
        return False
    except json.JSONDecodeError:
        print(f'✗ Erro ao decodificar JSON')
        return False
    except IOError as e:
        print(f'✗ Erro ao salvar arquivo: {e}')
        return False

if __name__ == '__main__':
    success = download_geojson()
    sys.exit(0 if success else 1)
