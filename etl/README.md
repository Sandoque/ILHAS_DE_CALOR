# ETL – Observatório Estadual de Ilhas de Calor – PE

This module ingests historical climate data from INMET, normalizes it to a canonical hourly schema, computes heat-related metrics, enriches geography, and loads results into PostgreSQL (`public.climate_hourly`).

## Architecture
- **ingest/**: download yearly ZIP archives from INMET, extract files, list expected years.
- **transform/**: normalize CSVs to canonical columns, compute heat metrics (apparent temperature, heat index, thermal amplitude, 7-day rolling mean), and enrich with geospatial metadata (mock IBGE lookup placeholder).
- **load/**: validate schema and append to PostgreSQL via SQLAlchemy.
- **pipeline/**: orchestrators for full and incremental runs plus CLI entrypoint.
- **utils/**: shared logger, timers, constants, and file helpers.

### Canonical schema
`date, hour_utc, temp_ins_c, temp_max_c, temp_min_c, humidity, wind_speed, radiation, precipitation, station_code, latitude, longitude, altitude, apparent_temperature, heat_index, thermal_amplitude, rolling_heat_7d, municipality`

## Running
Commands assume `python -m etl.pipeline.cli` from project root.

- Full load: `python -m etl.pipeline.cli run-full`
- Incremental: `python -m etl.pipeline.cli run-inc --year 2024` (omit `--year` to auto-detect missing years)

## Environment variables
- `INMET_BASE_URL` – URL pattern with `{year}` placeholder (default `https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip`).
- `DATA_DIR` – base data directory for raw/processed files (default `data/inmet`).
- `DATABASE_URL` – SQLAlchemy PostgreSQL URL (required for loading).
- Optional: `START_YEAR`, `END_YEAR`, `LOG_LEVEL`.

## Pipeline behavior
1. Determine year set (full list or missing years for incremental via DB query).
2. Download yearly ZIPs to `DATA_DIR/raw` and extract to `DATA_DIR/processed/{year}`.
3. Normalize CSVs (filter `UF=PE`) to canonical schema.
4. Compute heat metrics and 7-day rolling mean per station.
5. Enrich with municipality placeholder (TODO: integrate IBGE API).
6. Validate schema and load into `public.climate_hourly`.

## Output table
- Target: `public.climate_hourly`
- Load mode: append via `pandas.DataFrame.to_sql`
- Primary key/indices are not created here; manage in migrations if needed.

## Future improvements
- Replace mock geospatial enrichment with real IBGE API integration and caching.
- Add data quality checks (outlier detection, missing hours) and alerting.
- Persist intermediate parquet files for faster reprocessing and lineage.
- Parallelize per-year downloads/transforms for performance.
- Add automated tests and CI pipeline hooks.
