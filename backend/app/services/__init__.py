"""Service layer exports."""
from .climate_service import compute_trends, get_climate_by_station, get_daily_summary, list_years_available
from .station_service import get_station_details, list_stations
from .simulation_service import (
    simulate_future_heat_scenario,
    simulate_rainfall_change,
    simulate_temperature_increase,
)
from .analytics_service import (
    compute_heat_alerts,
    compute_rank_hottest_stations,
    compute_statewide_heat_map,
)

__all__ = [
    "get_climate_by_station",
    "get_daily_summary",
    "list_years_available",
    "compute_trends",
    "list_stations",
    "get_station_details",
    "simulate_temperature_increase",
    "simulate_rainfall_change",
    "simulate_future_heat_scenario",
    "compute_statewide_heat_map",
    "compute_rank_hottest_stations",
    "compute_heat_alerts",
]
