# Data Dictionary

## public.climate_hourly
Hourly climate facts ingested from INMET and enriched with metrics.

- `id` (int, PK): Surrogate key.
- `datetime_utc` (timestamp): Measurement datetime in UTC.
- `station_code` (text): INMET station identifier.
- `temperature` (float): Instant temperature (°C).
- `humidity` (float, %): Relative humidity.
- `wind_speed` (float, m/s): Wind speed.
- `radiation` (float, W/m²): Global radiation.
- `precipitation` (float, mm): Precipitation during the interval.
- `apparent_temperature` (float, °C): Steadman apparent temperature.
- `heat_index` (float, °C): NOAA heat index.
- `thermal_amplitude` (float, °C): Daily max − min.
- `rolling_heat_7d` (float, °C): 7-day rolling mean of apparent temperature.

Example usage: station time series, alerts, heat map aggregates.

## public.stations
Station dimension with geospatial attributes.

- `station_code` (text, PK): Station identifier.
- `name` (text): Station name.
- `uf` (text, 2-char): State.
- `latitude` (float): Lat coordinate.
- `longitude` (float): Lon coordinate.
- `altitude` (float, m): Altitude.
- `municipality` (text): Municipality name.

Used by: station metadata endpoints, map plotting.

## public.daily_metrics (materialized/aggregated)
Daily aggregates per station (produced by queries / views).

- `id` (int, PK)
- `date` (date): Day of record.
- `station_code` (text): Station identifier.
- `max_temp` (float, °C)
- `min_temp` (float, °C)
- `avg_temp` (float, °C)
- `heat_index_max` (float, °C)
- `thermal_amplitude` (float, °C)
- `precipitation_total` (float, mm)

Used by: `/api/climate/station/<code>/daily`, charts on city detail page.

## Other conceptual layers
- **Bronze raw files**: Extracted CSVs per year (not persisted in DB) used during ETL.
- **Silver normalized data**: Intermediate pandas DataFrames conforming to canonical schema before load.
- **Gold analytics**: Aggregations surfaced by analytics endpoints (heat map, hottest ranking, alerts) computed on-the-fly from `climate_hourly`.
