"""Run the MapBiomas ETL pipeline."""
from __future__ import annotations

from etl.mapbiomas.download_mapbiomas import download_xlsx
from etl.mapbiomas.extract_relevant_sheets import load_sheet
from etl.mapbiomas.filter_pernambuco import filter_state
from etl.mapbiomas.filter_municipios_inmet import filter_municipios
from etl.mapbiomas.normalize_mapbiomas import normalize
from etl.mapbiomas.load_to_postgres import load_mapbiomas
from etl.utils.logger import get_logger
from etl.utils.timers import time_block

logger = get_logger(__name__)


def run_mapbiomas() -> None:
    with time_block("mapbiomas_pipeline"):
        xlsx_path = download_xlsx()
        raw_df = load_sheet(xlsx_path)
        pe_df = filter_state(raw_df)
        muni_df = filter_municipios(pe_df)
        normalized = normalize(muni_df)
        load_mapbiomas(normalized)


if __name__ == "__main__":  # pragma: no cover
    run_mapbiomas()
