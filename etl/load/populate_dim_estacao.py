"""
Populate dim_estacao with weather stations from processed INMET CSV files.

Extracts unique weather stations from normalized INMET data and inserts them
into the dim_estacao dimension table.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from etl.utils.constants import DATA_DIR, DATABASE_URL
from etl.utils.logger import get_logger

logger = get_logger(__name__)


def _get_engine(database_url: Optional[str] = None) -> Engine:
    url = database_url or DATABASE_URL
    if not url:
        raise ValueError("DATABASE_URL is not set")
    return create_engine(url)


def _get_city_map(engine: Engine) -> dict[str, int]:
    """
    Map uppercase city name -> id_cidade from dim_cidade_pe.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT UPPER(nome_cidade), id_cidade FROM dim_cidade_pe"))
            return {row[0]: row[1] for row in result}
    except Exception:
        logger.warning("Could not load city map from dim_cidade_pe")
        return {}


def _parse_float_br(value: Optional[str]) -> Optional[float]:
    """Parse Brazilian-style float (uses comma as decimal separator)."""
    if not value:
        return None
    try:
        # Replace comma with period for standard float parsing
        return float(value.replace(",", "."))
    except ValueError:
        return None


def _extract_stations_from_csvs(data_dir: Optional[Path] = None) -> pd.DataFrame:
    """
    Extract unique weather stations from processed INMET CSV files.
    
    Returns DataFrame with columns: codigo_estacao, nome_estacao, latitude, longitude, altitude_m
    """
    data_dir = data_dir or DATA_DIR
    processed_dir = data_dir / "processed"
    
    stations_list = []
    
    # Iterate through all year subdirectories
    for year_dir in sorted(processed_dir.glob("*/")):
        if not year_dir.is_dir():
            continue
        
        logger.info("Processing stations from %s", year_dir.name)
        
        # Read all CSV files in the year directory - focus on NE/PE files
        for csv_file in (
            p
            for p in year_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() == ".csv"
            and "_PE_" in p.name.upper()
        ):
            try:
                # Read header rows to get station metadata
                # INMET CSVs have metadata in the first 8 rows (ends before "Data;Hora UTC;...")
                with open(csv_file, "r", encoding="iso-8859-1") as f:
                    lines = [f.readline() for _ in range(10)]
                
                # Parse metadata (format: KEY:;VALUE pairs)
                metadata = {}
                for line in lines:
                    if ":;" in line:
                        parts = line.strip().split(":;", 1)  # Split on first :;
                        if len(parts) == 2:
                            key = parts[0].strip().upper()
                            val = parts[1].strip()
                            metadata[key] = val
                
                # Extract station info
                # Handle different column names
                station_code = metadata.get("CODIGO (WMO)") or metadata.get("CD_ESTACAO") or metadata.get("CODIGO_ESTACAO")
                station_name = metadata.get("ESTACAO")
                uf = metadata.get("UF")
                latitude = metadata.get("LATITUDE")
                longitude = metadata.get("LONGITUDE")
                altitude = metadata.get("ALTITUDE")
                
                if station_code and station_name and uf == "PE":
                    stations_list.append({
                        "codigo_estacao": station_code.strip(),
                        "nome_estacao": station_name.strip(),
                        "municipio": station_name.strip(),
                        "uf": uf.strip(),
                        "latitude": _parse_float_br(latitude),
                        "longitude": _parse_float_br(longitude),
                        "altitude_m": _parse_float_br(altitude),
                    })
                    logger.info("Extracted station %s: %s (lat: %.2f, lon: %.2f)", 
                               station_code, station_name, 
                               _parse_float_br(latitude) or 0, 
                               _parse_float_br(longitude) or 0)
            
            except Exception:
                logger.warning("Failed to extract station info from %s", csv_file.name)
                continue
    
    # Remove duplicates based on codigo_estacao
    df_stations = pd.DataFrame(stations_list)
    if df_stations.empty:
        logger.warning("No PE stations found in processed INMET data")
        return pd.DataFrame()
    
    df_stations = df_stations.drop_duplicates(subset=["codigo_estacao"]).reset_index(drop=True)
    logger.info("Extracted %d unique stations from PE", len(df_stations))
    
    return df_stations


def _insert_stations_into_db(df_stations: pd.DataFrame, engine: Engine) -> int:
    """
    Insert extracted stations into dim_estacao table.
    
    Returns number of rows inserted.
    """
    if df_stations.empty:
        logger.warning("No stations to insert")
        return 0
    
    try:
        city_map = _get_city_map(engine)
        # Insert into dim_estacao using ON CONFLICT to handle duplicates
        with engine.connect() as conn:
            # Use raw SQL with ON CONFLICT DO NOTHING to avoid duplicates
            insert_sql = text("""
                INSERT INTO dim_estacao (codigo_estacao, nome_estacao, uf, municipio, id_cidade, latitude, longitude, altitude_m)
                VALUES (:codigo_estacao, :nome_estacao, :uf, :municipio, :id_cidade, :latitude, :longitude, :altitude_m)
                ON CONFLICT (codigo_estacao) DO UPDATE
                SET nome_estacao = EXCLUDED.nome_estacao,
                    municipio = COALESCE(dim_estacao.municipio, EXCLUDED.municipio),
                    id_cidade = COALESCE(dim_estacao.id_cidade, EXCLUDED.id_cidade),
                    latitude = COALESCE(dim_estacao.latitude, EXCLUDED.latitude),
                    longitude = COALESCE(dim_estacao.longitude, EXCLUDED.longitude),
                    altitude_m = COALESCE(dim_estacao.altitude_m, EXCLUDED.altitude_m)
            """)
            
            count = 0
            for _, row in df_stations.iterrows():
                try:
                    city_key = str(row["municipio"]).strip().upper()
                    id_cidade = city_map.get(city_key)
                    conn.execute(insert_sql, {
                        "codigo_estacao": row["codigo_estacao"],
                        "nome_estacao": row["nome_estacao"],
                        "uf": row.get("uf", "PE"),
                        "municipio": row.get("municipio"),
                        "id_cidade": id_cidade,
                        "latitude": row.get("latitude"),
                        "longitude": row.get("longitude"),
                        "altitude_m": row.get("altitude_m"),
                    })
                    count += 1
                except Exception:
                    logger.warning("Failed to insert station %s", row["codigo_estacao"])
                    continue
            
            conn.commit()

            # Fallback: if no city match, set id_cidade = id_estacao to keep non-null
            try:
                conn.execute(text("""
                    UPDATE dim_estacao
                    SET id_cidade = id_estacao
                    WHERE id_cidade IS NULL AND uf = 'PE'
                """))
                conn.commit()
            except Exception:
                logger.warning("Failed to backfill id_cidade with id_estacao")
            
            logger.info("Inserted %d stations into dim_estacao", count)
            return count
    
    except Exception:
        logger.exception("Failed to insert stations into database")
        return 0


def populate_dim_estacao(data_dir: Optional[Path] = None, engine: Optional[Engine] = None) -> int:
    """
    Main function to populate dim_estacao with stations from processed INMET data.
    
    Returns number of rows inserted.
    """
    logger.info("Starting dim_estacao population")
    
    # Extract stations from CSVs
    df_stations = _extract_stations_from_csvs(data_dir)
    
    if df_stations.empty:
        logger.error("No stations extracted; aborting population")
        return 0
    
    # Insert into database
    eng = engine or _get_engine()
    count = _insert_stations_into_db(df_stations, eng)
    
    logger.info("Completed dim_estacao population: %d rows inserted", count)
    return count


if __name__ == "__main__":  # pragma: no cover
    populate_dim_estacao()
