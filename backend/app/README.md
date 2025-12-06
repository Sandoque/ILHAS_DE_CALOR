# API – Observatorio Estadual de Ilhas de Calor – PE

Flask-based API exposing climate, station, simulation, and analytics endpoints backed by PostgreSQL data produced by the ETL module.

## Running locally
1. Install dependencies: `pip install -r backend/requirements.txt` (ensure Flask, Flask-SQLAlchemy, Flask-Marshmallow, Flask-Cors).
2. Set environment variables:
   - `DATABASE_URL` (PostgreSQL URL)
   - `SECRET_KEY` (optional)
   - `DEBUG` (optional, e.g., `1`)
3. Start the server: `flask --app backend.app:create_app --debug run` (from repo root) or `python -m flask --app backend.app:create_app run`.

CORS is enabled globally. No authentication is enforced yet.

## Endpoints
### Climate
- `GET /api/climate/station/<code>?start=ISO&end=ISO` – list climate records (max 5000) for a station between optional datetimes.
- `GET /api/climate/station/<code>/daily?limit=30` – aggregated daily summary for a station.
- `GET /api/climate/years` – list years available in the dataset.
- `GET /api/climate/<code>/trends` – basic trend stats for a station.

### Stations
- `GET /api/stations` – list stations.
- `GET /api/stations/<code>` – station metadata.

### Simulation
- `POST /api/simulation/temperature` – body `{ "station_code": "XXXX", "percentage": 5 }` adjusts recent temps by percentage.
- `POST /api/simulation/rainfall` – body `{ "station_code": "XXXX", "delta_mm": 10 }` adjusts rainfall.
- `POST /api/simulation/future` – body `{ "station_code": "XXXX", "climate_variables": {"temperature": 1.2, "humidity": 2} }` applies deltas.

### Analytics
- `GET /api/analytics/heatmap/<date>` – average apparent temperature and heat index per station for a date (YYYY-MM-DD).
- `GET /api/analytics/hottest?limit=10` – rank stations by peak apparent temperature.
- `GET /api/analytics/alerts?threshold=40` – records exceeding threshold apparent temperature.

### Web pages
- `/` index
- `/city/<code>` city detail view
- `/simulator` scenario playground

## Response format
- Success: `{ "success": true, "data": ... }`
- Error: `{ "success": false, "error": "message" }`

## Pagination
When pagination is used, responses include `items`, `page`, `per_page`, `total`, and `pages`. Default `page=1`, `per_page=20`; can be overridden via query params.

## Example curl requests
```bash
curl "http://localhost:5000/api/stations"
curl "http://localhost:5000/api/climate/station/A123?start=2024-01-01&end=2024-01-31"
curl "http://localhost:5000/api/climate/station/A123/daily?limit=7"
curl -X POST "http://localhost:5000/api/simulation/temperature" \
     -H "Content-Type: application/json" \
     -d '{"station_code": "A123", "percentage": 3}'
```

## Integration with ETL
The API reads from the same PostgreSQL database populated by the ETL module (`public.climate_hourly`, `stations`, `daily_metrics`). Run the ETL first to ensure data is available.

## Future improvements
- Add authentication/authorization and rate limiting.
- Add caching for hot endpoints (heat map, hottest stations).
- Expand analytics (anomaly detection, seasonal trends) and align with BI dashboards.
