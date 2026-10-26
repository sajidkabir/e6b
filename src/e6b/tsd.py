"""Time, speed, distance, and fuel: the slide-rule side of the E6B.

Distances are nautical miles, speeds are knots, times are minutes,
fuel is US gallons, and burn rates are US gallons per hour, unless a
function name says otherwise. Every function validates its inputs and
raises ValueError on a zero or negative divisor instead of returning
an infinite or meaningless answer.
"""


def time_min(distance_nm, ground_speed_kt):
    """Flight time in minutes for a distance at a ground speed."""
    if distance_nm < 0:
        raise ValueError("distance must not be negative")
    if ground_speed_kt <= 0:
        raise ValueError("ground speed must be positive")
    return distance_nm / ground_speed_kt * 60.0


def distance_nm(ground_speed_kt, time_minutes):
    """Distance covered at a ground speed in a given time."""
    if ground_speed_kt < 0:
        raise ValueError("ground speed must not be negative")
    if time_minutes < 0:
        raise ValueError("time must not be negative")
    return ground_speed_kt * time_minutes / 60.0


def ground_speed_kt(distance_nm, time_minutes):
    """Ground speed needed to cover a distance in a given time."""
    if distance_nm < 0:
        raise ValueError("distance must not be negative")
    if time_minutes <= 0:
        raise ValueError("time must be positive")
    return distance_nm / time_minutes * 60.0


def fuel_used_gal(burn_rate_gph, time_minutes):
    """Fuel used at a burn rate over a time in minutes."""
    if burn_rate_gph < 0:
        raise ValueError("burn rate must not be negative")
    if time_minutes < 0:
        raise ValueError("time must not be negative")
    return burn_rate_gph * time_minutes / 60.0


def endurance_min(fuel_gal, burn_rate_gph):
    """Endurance in minutes for a fuel quantity at a burn rate."""
    if fuel_gal < 0:
        raise ValueError("fuel must not be negative")
    if burn_rate_gph <= 0:
        raise ValueError("burn rate must be positive")
    return fuel_gal / burn_rate_gph * 60.0


def fuel_for_leg(distance_nm, ground_speed_kt, burn_rate_gph):
    """Fuel for one leg: time from distance and ground speed, then burn."""
    return fuel_used_gal(burn_rate_gph, time_min(distance_nm, ground_speed_kt))


def format_duration(time_minutes):
    """Format a duration as "1h 35.0m" or "45.0m" for short times."""
    if time_minutes < 0:
        raise ValueError("time must not be negative")
    hours = int(time_minutes // 60)
    minutes = time_minutes - hours * 60.0
    if hours:
        return "%dh %.1fm" % (hours, minutes)
    return "%.1fm" % minutes
