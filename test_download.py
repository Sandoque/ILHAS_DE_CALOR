#!/usr/bin/env python3
"""Test script to download missing years"""
from pathlib import Path
from etl.ingest.download_inmet import download_year
from etl.ingest.extract_zip import extract_year

# Check existing years
data_dir = Path('data/inmet/processed')
anos_existentes = sorted([int(d.name) for d in data_dir.iterdir() if d.is_dir()])
print(f"Anos disponíveis: {anos_existentes}")

anos_faltantes = [y for y in range(2010, 2025) if y not in anos_existentes]
print(f"Anos faltantes: {anos_faltantes}")

# Try to download each missing year
for year in anos_faltantes[:3]:  # Test first 3
    print(f"\n{'='*60}")
    print(f"Tentando baixar {year}...")
    try:
        result = download_year(year)
        print(f"✅ Download {year}: {result}")
        
        # Try to extract
        print(f"Tentando extrair {year}...")
        extracted = extract_year(year)
        print(f"✅ Extração {year}: {extracted} CSVs")
    except Exception as e:
        print(f"❌ Erro {year}: {type(e).__name__}: {e}")
