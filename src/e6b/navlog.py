"""Multi-leg navlogs: a wind solution, time, and fuel per leg.

A navlog is the E6B's end product for a VFR cross-country: one row
per leg, each with the heading that holds the course, the ground
speed the wind leaves you, the time the leg takes, and the fuel it
burns, plus running totals. Legs are plain data, so a navlog can be
stored as JSON and recomputed exactly.
"""

from dataclasses import dataclass

from e6b.tsd import fuel_used_gal, time_min
from e6b.wind import wind_correction


@dataclass(frozen=True)
class Leg:
    """One navlog leg, in the units the E6B works in."""

    name: str
    course_deg: float
    distance_nm: float
    tas_kt: float
    wind_from_deg: float
    wind_speed_kt: float
    fuel_flow_gph: float


@dataclass(frozen=True)
class ComputedLeg:
    """A leg with its wind solution, time, and fuel filled in."""

    leg: Leg
    heading_deg: float
    wca_deg: float
    ground_speed_kt: float
    headwind_kt: float
    crosswind_kt: float
    time_min: float
    fuel_gal: float


@dataclass(frozen=True)
class NavlogResult:
    """A computed navlog: per-leg rows plus totals."""

    legs: tuple
    total_distance_nm: float = 0.0
    total_time_min: float = 0.0
    total_fuel_gal: float = 0.0


def compute_navlog(legs):
    """Compute every leg of a navlog and total distance, time, and fuel."""
    computed = []
    for leg in legs:
        if leg.distance_nm < 0:
            raise ValueError("leg %r has a negative distance" % leg.name)
        if leg.fuel_flow_gph < 0:
            raise ValueError("leg %r has a negative fuel flow" % leg.name)
        solution = wind_correction(
            leg.course_deg, leg.tas_kt, leg.wind_from_deg, leg.wind_speed_kt
        )
        minutes = time_min(leg.distance_nm, solution.ground_speed)
        fuel = fuel_used_gal(leg.fuel_flow_gph, minutes)
        computed.append(
            ComputedLeg(
                leg=leg,
                heading_deg=solution.heading_deg,
                wca_deg=solution.wca_deg,
                ground_speed_kt=solution.ground_speed,
                headwind_kt=solution.headwind,
                crosswind_kt=solution.crosswind,
                time_min=minutes,
                fuel_gal=fuel,
            )
        )
    return NavlogResult(
        legs=tuple(computed),
        total_distance_nm=sum(row.leg.distance_nm for row in computed),
        total_time_min=sum(row.time_min for row in computed),
        total_fuel_gal=sum(row.fuel_gal for row in computed),
    )


def navlog_from_json(data):
    """Build a leg list from parsed JSON: a list of leg objects.

    Each object needs name, course_deg, distance_nm, tas_kt,
    wind_from_deg, wind_speed_kt, and fuel_flow_gph. Missing keys
    raise ValueError with the leg index, not a bare KeyError.
    """
    if not isinstance(data, list):
        raise ValueError("navlog JSON must be a list of legs")
    legs = []
    for index, item in enumerate(data):
        try:
            legs.append(
                Leg(
                    name=str(item["name"]),
                    course_deg=float(item["course_deg"]),
                    distance_nm=float(item["distance_nm"]),
                    tas_kt=float(item["tas_kt"]),
                    wind_from_deg=float(item["wind_from_deg"]),
                    wind_speed_kt=float(item["wind_speed_kt"]),
                    fuel_flow_gph=float(item["fuel_flow_gph"]),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("leg %d is missing or has a bad field: %s" % (index, exc))
    return legs


def navlog_table(result):
    """Render a computed navlog as a plain-text table with totals."""
    header = (
        "%-22s %6s %6s %6s %6s %7s %6s" % ("Leg", "Course", "Head", "GS", "Time", "Fuel", "Dist")
    )
    lines = [header]
    for row in result.legs:
        lines.append(
            "%-22s %6.0f %6.0f %6.0f %6.1f %7.1f %6.0f"
            % (
                row.leg.name[:22],
                row.leg.course_deg,
                row.heading_deg,
                row.ground_speed_kt,
                row.time_min,
                row.fuel_gal,
                row.leg.distance_nm,
            )
        )
    lines.append(
        "%-22s %6s %6s %6s %6.1f %7.1f %6.0f"
        % (
            "TOTAL",
            "",
            "",
            "",
            result.total_time_min,
            result.total_fuel_gal,
            result.total_distance_nm,
        )
    )
    return "\n".join(lines)
