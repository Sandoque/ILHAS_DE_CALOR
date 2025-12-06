# Architecture Overview

## High-level flow
1. **Ingest (ETL)**: Yearly INMET ZIP archives are downloaded (`etl/ingest`), extracted, filtered to Pernambuco, and normalized to a canonical schema.
2. **Transform**: Heat metrics (apparent temperature, heat index, thermal amplitude, rolling 7d) are computed; geospatial enrichment adds municipality placeholders.
3. **Load**: Data is validated and appended into PostgreSQL (`public.climate_hourly`) alongside station metadata tables.
4. **API**: Flask app (backend/app) exposes services and blueprints that read from PostgreSQL via SQLAlchemy and serialize with Marshmallow.
5. **Front-end**: Tailwind/HTMX/ECharts templates render dashboards, station detail views, and the simulator. HTMX fetches API JSON, ECharts renders charts.

## Data flow details
- **Bronze → Silver → Gold (conceptually)**: Raw CSVs (bronze) are normalized (silver) and enriched/aggregated (gold-like) through metrics and daily summaries used by analytics endpoints.
- **ETL pipeline**: `run_full_pipeline.py` orchestrates download → extract → normalize → metric calc → geo enrich → schema validate → load. `run_incremental.py` checks missing years in DB to avoid duplicates.
- **API services**: `services/*.py` encapsulate queries (climate series, daily summaries, trends, heat alerts). Routes in `routes/api_*.py` return JSON consumed by HTMX or fetch().
- **Templates**: `templates/*.html` include reusable components and load ECharts; they call endpoints like `/api/analytics/heatmap/<date>` for map visuals and `/api/climate/station/<code>/daily` for station charts.

## Container orchestration
- **docker-compose** runs PostgreSQL and the Flask backend (`web`). The backend connects via `DATABASE_URL=postgresql://ilhas_user:ilhas_pass@postgres:5432/ilhas_de_calor` inside the Compose network.
- The backend container uses gunicorn on port 8000; Postgres stays on its mapped port (5433 → 5432) for host access.
