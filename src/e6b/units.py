"""Unit conversions for the slide rule: speed, distance, volume, fuel mass.

Exact constants: 1 nautical mile is 1852 metres, 1 statute mile is
1609.344 metres, 1 US gallon is 3.785411784 litres. Fuel mass uses a
caller-supplied pounds-per-gallon figure because avgas (about 6.0) and
Jet A (about 6.7 to 6.8) differ, and the exact figure belongs to the
aircraft manual, not to this library. The default 6.0 is avgas.
"""

KT_TO_KMH = 1.852
KT_TO_MPH = 1.150779448
KT_TO_MS = 0.514444444
NM_TO_KM = 1.852
NM_TO_SM = 1.150779448
USGAL_TO_LITRES = 3.785411784

_SPEED_TO_KT = {
    "kt": 1.0,
    "kmh": 1.0 / KT_TO_KMH,
    "mph": 1.0 / KT_TO_MPH,
    "ms": 1.0 / KT_TO_MS,
}

_DISTANCE_TO_NM = {
    "nm": 1.0,
    "km": 1.0 / NM_TO_KM,
    "sm": 1.0 / NM_TO_SM,
    "m": 1.0 / 1852.0,
}

_VOLUME_TO_USGAL = {
    "gal": 1.0,
    "usgal": 1.0,
    "l": 1.0 / USGAL_TO_LITRES,
    "litres": 1.0 / USGAL_TO_LITRES,
    "liters": 1.0 / USGAL_TO_LITRES,
}


def kt_to_kmh(speed_kt):
    return speed_kt * KT_TO_KMH


def kmh_to_kt(speed_kmh):
    return speed_kmh / KT_TO_KMH


def kt_to_mph(speed_kt):
    return speed_kt * KT_TO_MPH


def mph_to_kt(speed_mph):
    return speed_mph / KT_TO_MPH


def kt_to_ms(speed_kt):
    return speed_kt * KT_TO_MS


def ms_to_kt(speed_ms):
    return speed_ms / KT_TO_MS


def nm_to_km(distance_nm):
    return distance_nm * NM_TO_KM


def km_to_nm(distance_km):
    return distance_km / NM_TO_KM


def nm_to_sm(distance_nm):
    return distance_nm * NM_TO_SM


def sm_to_nm(distance_sm):
    return distance_sm / NM_TO_SM


def usgal_to_litres(volume_usgal):
    return volume_usgal * USGAL_TO_LITRES


def litres_to_usgal(volume_litres):
    return volume_litres / USGAL_TO_LITRES


def fuel_weight_lb(volume_usgal, pounds_per_gallon=6.0):
    """Fuel weight in pounds. Default 6.0 lb per US gallon (avgas)."""
    if volume_usgal < 0:
        raise ValueError("fuel volume must not be negative")
    if pounds_per_gallon <= 0:
        raise ValueError("pounds per gallon must be positive")
    return volume_usgal * pounds_per_gallon


def convert_speed(value, from_unit, to_unit):
    """Convert a speed between kt, kmh, mph, and ms."""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    if from_unit not in _SPEED_TO_KT or to_unit not in _SPEED_TO_KT:
        raise ValueError("unknown speed unit: use kt, kmh, mph, or ms")
    in_kt = value * _SPEED_TO_KT[from_unit]
    if to_unit == "kt":
        return in_kt
    if to_unit == "kmh":
        return in_kt * KT_TO_KMH
    if to_unit == "mph":
        return in_kt * KT_TO_MPH
    return in_kt * KT_TO_MS


def convert_distance(value, from_unit, to_unit):
    """Convert a distance between nm, km, sm, and m."""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    if from_unit not in _DISTANCE_TO_NM or to_unit not in _DISTANCE_TO_NM:
        raise ValueError("unknown distance unit: use nm, km, sm, or m")
    in_nm = value * _DISTANCE_TO_NM[from_unit]
    if to_unit == "nm":
        return in_nm
    if to_unit == "km":
        return in_nm * NM_TO_KM
    if to_unit == "sm":
        return in_nm * NM_TO_SM
    return in_nm * 1852.0


def convert_volume(value, from_unit, to_unit):
    """Convert a volume between gal (US gallons) and l (litres)."""
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    if from_unit not in _VOLUME_TO_USGAL or to_unit not in _VOLUME_TO_USGAL:
        raise ValueError("unknown volume unit: use gal or l")
    in_gal = value * _VOLUME_TO_USGAL[from_unit]
    if to_unit in ("gal", "usgal"):
        return in_gal
    return in_gal * USGAL_TO_LITRES
