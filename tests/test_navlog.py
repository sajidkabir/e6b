import pytest

from e6b import Leg, compute_navlog, navlog_from_json, navlog_table


def _legs():
    return [
        Leg("Alpha to Bravo", 90, 60, 120, 230, 18, 10.0),
        Leg("Bravo to Charlie", 180, 120, 120, 270, 12, 10.0),
    ]


def test_navlog_totals_match_leg_sums():
    result = compute_navlog(_legs())
    assert len(result.legs) == 2
    assert result.total_distance_nm == pytest.approx(180)
    assert result.total_time_min == pytest.approx(
        sum(row.time_min for row in result.legs)
    )
    assert result.total_fuel_gal == pytest.approx(
        sum(row.fuel_gal for row in result.legs)
    )


def test_navlog_first_leg_uses_wind_solution():
    # Leg 1 flies TAS 120 (not the 125 of the textbook example), so
    # heading 96 and ground speed 133 are the correct answers here.
    result = compute_navlog(_legs())
    first = result.legs[0]
    assert first.heading_deg == pytest.approx(96, abs=1.0)
    assert first.ground_speed_kt == pytest.approx(133, abs=1.0)
    assert first.time_min == pytest.approx(60 / 133 * 60, abs=0.5)


def test_navlog_second_leg_pure_crosswind():
    result = compute_navlog(_legs())
    second = result.legs[1]
    assert second.heading_deg == pytest.approx(186, abs=1.0)
    assert second.crosswind_kt == pytest.approx(12)


def test_empty_navlog_is_zero():
    result = compute_navlog([])
    assert result.legs == ()
    assert result.total_distance_nm == 0
    assert result.total_time_min == 0
    assert result.total_fuel_gal == 0


def test_navlog_bad_legs_rejected():
    with pytest.raises(ValueError):
        compute_navlog([Leg("Bad", 90, -10, 120, 0, 0, 10.0)])
    with pytest.raises(ValueError):
        compute_navlog([Leg("Bad", 90, 10, 120, 0, 0, -1.0)])
    with pytest.raises(ValueError):
        # Course 180 with wind 270/200 is a pure 200 kt crosswind,
        # stronger than the 120 kt TAS, so no heading holds the course.
        compute_navlog([Leg("Bad", 180, 10, 120, 270, 200, 10.0)])


def test_navlog_from_json():
    data = [
        {
            "name": "Alpha to Bravo",
            "course_deg": 90,
            "distance_nm": 60,
            "tas_kt": 120,
            "wind_from_deg": 230,
            "wind_speed_kt": 18,
            "fuel_flow_gph": 10.0,
        }
    ]
    legs = navlog_from_json(data)
    assert legs[0].name == "Alpha to Bravo"
    assert legs[0].tas_kt == 120


def test_navlog_from_json_rejects_bad_data():
    with pytest.raises(ValueError):
        navlog_from_json({"not": "a list"})
    with pytest.raises(ValueError):
        navlog_from_json([{"name": "Half a leg"}])


def test_navlog_table_shows_totals():
    result = compute_navlog(_legs())
    table = navlog_table(result)
    assert "TOTAL" in table
    assert "Alpha to Bravo" in table
    assert "Bravo to Charlie" in table
    lines = table.splitlines()
    assert len(lines) == 4  # header, two legs, totals
