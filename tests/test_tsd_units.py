import pytest

from e6b import (
    convert_distance,
    convert_speed,
    convert_volume,
    distance_nm,
    endurance_min,
    format_duration,
    fuel_for_leg,
    fuel_used_gal,
    fuel_weight_lb,
    ground_speed_kt,
    kmh_to_kt,
    kt_to_kmh,
    kt_to_mph,
    kt_to_ms,
    litres_to_usgal,
    nm_to_km,
    time_min,
    usgal_to_litres,
)


def test_time_speed_distance_triangle():
    assert time_min(300, 190) == pytest.approx(94.7, abs=0.1)
    assert distance_nm(190, 94.736842) == pytest.approx(300, abs=0.01)
    assert ground_speed_kt(300, 94.736842) == pytest.approx(190, abs=0.01)


def test_tsd_zero_distance_is_zero_time():
    assert time_min(0, 100) == 0


def test_tsd_bad_inputs_rejected():
    with pytest.raises(ValueError):
        time_min(100, 0)
    with pytest.raises(ValueError):
        time_min(-10, 100)
    with pytest.raises(ValueError):
        ground_speed_kt(100, 0)
    with pytest.raises(ValueError):
        distance_nm(100, -5)


def test_fuel_math():
    # The slide-rule example: 20 gal/hr for 51 minutes is 17 gallons.
    assert fuel_used_gal(20, 51) == pytest.approx(17, abs=0.01)
    assert endurance_min(17, 20) == pytest.approx(51, abs=0.01)
    assert fuel_for_leg(190, 95, 10) == pytest.approx(20, abs=0.01)


def test_fuel_bad_inputs_rejected():
    with pytest.raises(ValueError):
        fuel_used_gal(10, -1)
    with pytest.raises(ValueError):
        endurance_min(10, 0)


def test_format_duration():
    assert format_duration(45) == "45.0m"
    assert format_duration(95) == "1h 35.0m"
    assert format_duration(0) == "0.0m"
    with pytest.raises(ValueError):
        format_duration(-1)


def test_speed_conversions():
    assert kt_to_kmh(100) == pytest.approx(185.2)
    assert kmh_to_kt(185.2) == pytest.approx(100)
    assert kt_to_mph(100) == pytest.approx(115.08, abs=0.01)
    assert kt_to_ms(100) == pytest.approx(51.44, abs=0.01)
    assert convert_speed(100, "kt", "kmh") == pytest.approx(185.2)
    assert convert_speed(185.2, "kmh", "kt") == pytest.approx(100)
    assert convert_speed(100, "mph", "kt") == pytest.approx(86.9, abs=0.1)
    with pytest.raises(ValueError):
        convert_speed(100, "kt", "furlongs")


def test_distance_conversions():
    assert nm_to_km(80) == pytest.approx(148.16)
    assert convert_distance(80, "km", "nm") == pytest.approx(43.2, abs=0.1)
    assert convert_distance(100, "nm", "sm") == pytest.approx(115.08, abs=0.01)
    assert convert_distance(1852, "m", "nm") == pytest.approx(1.0)
    with pytest.raises(ValueError):
        convert_distance(10, "nm", "parsecs")


def test_volume_and_fuel_weight():
    assert usgal_to_litres(10) == pytest.approx(37.854, abs=0.001)
    assert litres_to_usgal(37.85411784) == pytest.approx(10, abs=1e-6)
    assert convert_volume(10, "gal", "l") == pytest.approx(37.854, abs=0.001)
    assert fuel_weight_lb(10) == pytest.approx(60.0)
    assert fuel_weight_lb(10, pounds_per_gallon=6.7) == pytest.approx(67.0)
    with pytest.raises(ValueError):
        fuel_weight_lb(-1)
    with pytest.raises(ValueError):
        convert_volume(10, "gal", "barrels")
