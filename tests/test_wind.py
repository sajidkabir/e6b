import pytest

from e6b import (
    ground_vector,
    normalize_angle,
    solve_wind,
    to_magnetic,
    to_true,
    wind_components,
    wind_correction,
)


def test_normalize_angle():
    assert normalize_angle(360) == 0
    assert normalize_angle(-10) == 350
    assert normalize_angle(725) == 5
    assert normalize_angle(0) == 0


def test_textbook_wind_correction_first_example():
    # Sportys/ASA style problem: course 180, TAS 120, wind 270/12.
    # Published answer: WCA 6 deg right, heading 186, ground speed 119.
    solution = wind_correction(180, 120, 270, 12)
    assert solution.heading_deg == pytest.approx(186, abs=1.0)
    assert solution.wca_deg == pytest.approx(6, abs=1.0)
    assert solution.ground_speed == pytest.approx(119, abs=1.0)
    assert solution.headwind == pytest.approx(0, abs=0.1)
    assert solution.crosswind == pytest.approx(12, abs=0.1)


def test_textbook_wind_correction_second_example():
    # Course 090, TAS 125, wind 230/18. Published answer: heading 095, GS 138.
    solution = wind_correction(90, 125, 230, 18)
    assert solution.heading_deg == pytest.approx(95, abs=1.0)
    assert solution.ground_speed == pytest.approx(138, abs=1.0)


def test_no_wind_is_identity():
    solution = wind_correction(90, 100, 0, 0)
    assert solution.heading_deg == 90
    assert solution.ground_speed == pytest.approx(100)
    assert solution.wca_deg == 0


def test_pure_headwind_slows_you_down():
    solution = wind_correction(180, 100, 180, 20)
    assert solution.heading_deg == 180
    assert solution.ground_speed == pytest.approx(80)
    assert solution.headwind == pytest.approx(20)


def test_pure_tailwind_speeds_you_up():
    solution = wind_correction(180, 100, 0, 20)
    assert solution.heading_deg == 180
    assert solution.ground_speed == pytest.approx(120)
    assert solution.headwind == pytest.approx(-20)


def test_left_crosswind_corrects_left():
    solution = wind_correction(180, 100, 90, 10)
    assert solution.wca_deg < 0
    assert solution.heading_deg == pytest.approx(180 + solution.wca_deg)


def test_round_trip_wind_correction_then_track():
    solution = wind_correction(90, 125, 230, 18)
    track, gs = ground_vector(solution.heading_deg, 125, 230, 18)
    assert track == pytest.approx(90, abs=1e-6)
    assert gs == pytest.approx(solution.ground_speed, abs=1e-6)


def test_crosswind_sign_convention():
    # Runway 18 (facing south), wind from the west: from the right.
    headwind, crosswind = wind_components(180, 270, 15)
    assert headwind == pytest.approx(0, abs=1e-9)
    assert crosswind == pytest.approx(15)
    # Wind from the east: from the left.
    _, crosswind = wind_components(180, 90, 15)
    assert crosswind == pytest.approx(-15)


def test_crosswind_limit_rule():
    # A 15 kt crosswind on runway 18 with wind 270/15 is all crosswind.
    _, crosswind = wind_components(180, 270, 15)
    assert abs(crosswind) == 15


def test_impossible_course_rejected():
    with pytest.raises(ValueError):
        wind_correction(180, 50, 270, 60)


def test_negative_inputs_rejected():
    with pytest.raises(ValueError):
        wind_correction(180, 0, 270, 10)
    with pytest.raises(ValueError):
        wind_correction(180, 100, 270, -5)
    with pytest.raises(ValueError):
        wind_components(180, 270, -1)


def test_solve_wind_textbook_reverse_problem():
    # Course 180, heading 160, TAS 140, GS 120: published wind 104/50.
    wind_from, wind_speed = solve_wind(180, 160, 140, 120)
    assert wind_from == pytest.approx(104, abs=1.0)
    assert wind_speed == pytest.approx(49, abs=1.0)


def test_solve_wind_round_trip():
    solution = wind_correction(45, 110, 300, 25)
    wind_from, wind_speed = solve_wind(
        solution.course_deg, solution.heading_deg, 110, solution.ground_speed
    )
    assert wind_from == pytest.approx(300, abs=1e-6)
    assert wind_speed == pytest.approx(25, abs=1e-6)


def test_solve_wind_calm():
    wind_from, wind_speed = solve_wind(90, 90, 100, 100)
    assert wind_speed == pytest.approx(0, abs=1e-9)


def test_ground_vector_zero_speed_rejected():
    # Heading north at 50 kt against a 50 kt wind from the north
    # (blowing south) leaves zero ground speed, so track is undefined.
    with pytest.raises(ValueError):
        ground_vector(0, 50, 0, 50)


def test_magnetic_conversions():
    # 10 degrees east variation: magnetic is 10 less than true.
    assert to_magnetic(90, 10) == 80
    assert to_true(80, 10) == 90
    # West variation is negative east: magnetic is more than true.
    assert to_magnetic(90, -5) == 95
    assert to_true(95, -5) == 90
    # Wrap-around: true 005 with 10 east gives magnetic 355.
    assert to_magnetic(5, 10) == 355
