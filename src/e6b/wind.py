"""Wind triangle mathematics, the wind side of the E6B.

Conventions, stated once so nothing is ambiguous:

- All bearings are degrees clockwise from true north, 0 to 360.
- Wind direction is the direction the wind comes FROM, as reported in
  METARs, TAFs, and winds-aloft forecasts.
- Headwind is positive when the wind opposes the course; a negative
  headwind is a tailwind of the same magnitude.
- Crosswind is positive when the wind comes from the right of the
  course (or runway heading), negative when it comes from the left.
- Wind correction angle (WCA) is positive to the right: heading is
  course plus WCA. To hold a course against a crosswind, point the nose
  into the wind, which is the side the wind comes from.
- Magnetic variation is given as degrees east (positive) or west
  (negative): magnetic north sits that far east of true north when
  the value is positive. Magnetic heading equals true heading minus
  east variation ("east is least, west is best" for the correction).
"""

import math
from dataclasses import dataclass


def normalize_angle(angle_deg):
    """Normalize any bearing to the range [0, 360)."""
    angle = math.fmod(angle_deg, 360.0)
    if angle < 0:
        angle += 360.0
    if angle == 360.0:  # fmod edge case for exact multiples
        angle = 0.0
    return angle


def _unit_vector(bearing_deg):
    """Unit vector (east, north) for a bearing in degrees."""
    rad = math.radians(bearing_deg)
    return math.sin(rad), math.cos(rad)


def wind_components(course_deg, wind_from_deg, wind_speed):
    """Headwind and crosswind components for a course or runway heading.

    Returns (headwind_kt, crosswind_kt) in the same speed units as
    wind_speed. Headwind is positive against the course; crosswind is
    positive from the right. A negative wind speed is rejected.
    """
    if wind_speed < 0:
        raise ValueError("wind speed must not be negative")
    diff = math.radians(normalize_angle(wind_from_deg - course_deg))
    headwind = wind_speed * math.cos(diff)
    crosswind = wind_speed * math.sin(diff)
    return headwind, crosswind


@dataclass(frozen=True)
class WindSolution:
    """One solved wind triangle: hold this heading to fly this course."""

    course_deg: float
    tas: float
    wind_from_deg: float
    wind_speed: float
    heading_deg: float
    wca_deg: float
    ground_speed: float
    headwind: float
    crosswind: float


def wind_correction(course_deg, tas, wind_from_deg, wind_speed):
    """Solve the classic E6B wind problem.

    Given the desired true course, true airspeed, and wind (from
    direction and speed), return the true heading to fly and the
    resulting ground speed. Raises ValueError if the crosswind
    component exceeds TAS, in which case no heading can hold the
    course, or if TAS is not positive.
    """
    if tas <= 0:
        raise ValueError("true airspeed must be positive")
    if wind_speed < 0:
        raise ValueError("wind speed must not be negative")
    course = normalize_angle(course_deg)
    wind_from = normalize_angle(wind_from_deg)
    headwind, crosswind = wind_components(course, wind_from, wind_speed)
    ratio = crosswind / tas
    if abs(ratio) > 1.0:
        raise ValueError(
            "crosswind component %.1f exceeds true airspeed %.1f: "
            "no heading can hold this course" % (crosswind, tas)
        )
    wca = math.degrees(math.asin(ratio))
    heading = normalize_angle(course + wca)
    ground_speed = tas * math.cos(math.radians(wca)) - headwind
    return WindSolution(
        course_deg=course,
        tas=tas,
        wind_from_deg=wind_from,
        wind_speed=wind_speed,
        heading_deg=heading,
        wca_deg=wca,
        ground_speed=ground_speed,
        headwind=headwind,
        crosswind=crosswind,
    )


def ground_vector(heading_deg, tas, wind_from_deg, wind_speed):
    """Track and ground speed for a heading actually flown.

    The inverse of wind_correction: instead of asking what heading
    holds a course, this asks where a given heading actually takes
    you. Returns (track_deg, ground_speed). Raises ValueError if the
    ground speed is zero, since the track is then undefined.
    """
    if tas <= 0:
        raise ValueError("true airspeed must be positive")
    if wind_speed < 0:
        raise ValueError("wind speed must not be negative")
    air_east, air_north = _unit_vector(heading_deg)
    wind_to = normalize_angle(wind_from_deg + 180.0)
    wind_east, wind_north = _unit_vector(wind_to)
    east = tas * air_east + wind_speed * wind_east
    north = tas * air_north + wind_speed * wind_north
    ground_speed = math.hypot(east, north)
    if ground_speed < 1e-9:
        raise ValueError("ground speed is zero: track is undefined")
    track = normalize_angle(math.degrees(math.atan2(east, north)))
    return track, ground_speed


def solve_wind(course_deg, heading_deg, tas, ground_speed):
    """Recover the wind from a flown triangle (the E6B reverse problem).

    Given the true course held, the true heading flown, TAS, and the
    observed ground speed, return (wind_from_deg, wind_speed). This
    is the textbook problem: course 180, heading 160, TAS 140,
    ground speed 120 gives wind from about 104 degrees at about
    49 knots.
    """
    if tas <= 0:
        raise ValueError("true airspeed must be positive")
    if ground_speed < 0:
        raise ValueError("ground speed must not be negative")
    ground_east, ground_north = _unit_vector(course_deg)
    air_east, air_north = _unit_vector(heading_deg)
    wind_east = ground_speed * ground_east - tas * air_east
    wind_north = ground_speed * ground_north - tas * air_north
    speed = math.hypot(wind_east, wind_north)
    if speed < 1e-9:
        return 0.0, 0.0
    wind_to = normalize_angle(math.degrees(math.atan2(wind_east, wind_north)))
    wind_from = normalize_angle(wind_to + 180.0)
    return wind_from, speed


def to_magnetic(true_deg, variation_east_deg):
    """True heading to magnetic heading for an east-positive variation."""
    return normalize_angle(true_deg - variation_east_deg)


def to_true(magnetic_deg, variation_east_deg):
    """Magnetic heading to true heading for an east-positive variation."""
    return normalize_angle(magnetic_deg + variation_east_deg)
