# API Reference

Base URL: `http://localhost:8000`

## Stations
- `GET /api/stations`
  - Returns all stations metadata.
  - Used by: simulator select (fetch), map overlays.
- `GET /api/stations/<code>`
  - Station metadata detail.
  - Used by: city detail metadata panel.

## Climate
- `GET /api/climate/station/<code>?start=ISO&end=ISO`
  - Hourly climate records (limited to 5000) filtered by date range.
  - Used by: potential deep dives, simulations.
- `GET /api/climate/station/<code>/daily?limit=30`
  - Daily aggregates (max/min/avg temp, heat index max, thermal amplitude, precipitation total).
  - Used by: city detail cards/table and charts.
- `GET /api/climate/years`
  - Distinct years available in dataset.
  - Used by: dashboard summaries.
- `GET /api/climate/<code>/trends`
  - Basic trend stats per station (avg/max/min temp, humidity, wind).
  - Used by: insights panels.

## Analytics
- `GET /api/analytics/heatmap/<date>`
  - Avg apparent temperature/heat index per station for a date (YYYY-MM-DD).
  - Used by: index heatmap (ECharts scatter).
- `GET /api/analytics/hottest?limit=10`
  - Ranking of stations by peak apparent temperature.
  - Used by: index ranking chart/table; headline cards.
- `GET /api/analytics/alerts?threshold=40`
  - Records exceeding heat threshold.
  - Used by: dashboard metric for amplitude/alerts.

## Simulation
- `POST /api/simulation/temperature`
  - Body: `{ "station_code": "A123", "percentage": 5 }`
  - Adjusts recent temperature metrics by percentage.
- `POST /api/simulation/rainfall`
  - Body: `{ "station_code": "A123", "delta_mm": 10 }`
  - Adjusts recent precipitation.
- `POST /api/simulation/future`
  - Body: `{ "station_code": "A123", "climate_variables": { "temperature": 1.2, "humidity": 2, "precipitation": -3 } }`
  - Used by: simulator form via HTMX/fetch to project scenarios.

## Response format
- Success: `{ "success": true, "data": ... }`
- Error: `{ "success": false, "error": "message" }`

## Examples
```bash
curl "http://localhost:8000/api/stations"
curl "http://localhost:8000/api/climate/station/A123/daily?limit=7"
curl "http://localhost:8000/api/analytics/heatmap/2024-01-15"
curl -X POST "http://localhost:8000/api/simulation/future" \
  -H "Content-Type: application/json" \
  -d '{"station_code": "A123", "climate_variables": {"temperature": 1.0}}'
```
