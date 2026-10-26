"""e6b: a pip-installable E6B flight computer in pure Python.

Wind triangle solutions, crosswind components, time-speed-distance,
fuel planning, unit conversions, and multi-leg navlogs, with a CLI.
Zero dependencies, standard library only.
"""

from e6b.navlog import ComputedLeg, Leg, NavlogResult, compute_navlog, navlog_from_json, navlog_table
from e6b.tsd import (
    distance_nm,
    endurance_min,
    format_duration,
    fuel_for_leg,
    fuel_used_gal,
    ground_speed_kt,
    time_min,
)
from e6b.units import (
    convert_distance,
    convert_speed,
    convert_volume,
    fuel_weight_lb,
    kmh_to_kt,
    km_to_nm,
    kt_to_kmh,
    kt_to_mph,
    kt_to_ms,
    litres_to_usgal,
    mph_to_kt,
    ms_to_kt,
    nm_to_km,
    nm_to_sm,
    sm_to_nm,
    usgal_to_litres,
)
from e6b.wind import (
    WindSolution,
    ground_vector,
    normalize_angle,
    solve_wind,
    to_magnetic,
    to_true,
    wind_components,
    wind_correction,
)

__version__ = "0.1.0"

__all__ = [
    "ComputedLeg",
    "Leg",
    "NavlogResult",
    "WindSolution",
    "compute_navlog",
    "convert_distance",
    "convert_speed",
    "convert_volume",
    "distance_nm",
    "endurance_min",
    "format_duration",
    "fuel_for_leg",
    "fuel_used_gal",
    "fuel_weight_lb",
    "ground_speed_kt",
    "ground_vector",
    "kmh_to_kt",
    "km_to_nm",
    "kt_to_kmh",
    "kt_to_mph",
    "kt_to_ms",
    "litres_to_usgal",
    "mph_to_kt",
    "ms_to_kt",
    "navlog_from_json",
    "navlog_table",
    "nm_to_km",
    "nm_to_sm",
    "normalize_angle",
    "sm_to_nm",
    "solve_wind",
    "time_min",
    "to_magnetic",
    "to_true",
    "usgal_to_litres",
    "wind_components",
    "wind_correction",
]
