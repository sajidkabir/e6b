import json

import pytest

from e6b.cli import main


def test_cli_wind(capsys):
    assert main(["wind", "--course", "90", "--tas", "125", "--wind-from", "230", "--wind-speed", "18"]) == 0
    out = capsys.readouterr().out
    assert "95" in out
    assert "138" in out


def test_cli_crosswind(capsys):
    assert main(["crosswind", "--runway", "180", "--wind-from", "270", "--wind-speed", "15"]) == 0
    out = capsys.readouterr().out
    assert "+15" in out or "15" in out


def test_cli_solve_wind(capsys):
    assert main(["solve-wind", "--course", "180", "--heading", "160", "--tas", "140", "--gs", "120"]) == 0
    out = capsys.readouterr().out
    assert "104" in out


def test_cli_track(capsys):
    assert main(["track", "--heading", "95", "--tas", "125", "--wind-from", "230", "--wind-speed", "18"]) == 0
    out = capsys.readouterr().out
    assert "90" in out


def test_cli_tsd_all_three_forms(capsys):
    assert main(["tsd", "--distance", "300", "--gs", "190"]) == 0
    assert "94.7" in capsys.readouterr().out
    assert main(["tsd", "--gs", "190", "--time", "94.736842"]) == 0
    assert "300.0" in capsys.readouterr().out
    assert main(["tsd", "--distance", "300", "--time", "94.736842"]) == 0
    assert "190.0" in capsys.readouterr().out


def test_cli_tsd_needs_two_args(capsys):
    assert main(["tsd", "--distance", "300"]) == 2


def test_cli_fuel_both_forms(capsys):
    assert main(["fuel", "--rate", "20", "--time", "51"]) == 0
    assert "17.0" in capsys.readouterr().out
    assert main(["fuel", "--rate", "20", "--fuel", "17"]) == 0
    assert "51.0" in capsys.readouterr().out


def test_cli_fuel_needs_one_form(capsys):
    assert main(["fuel", "--rate", "20"]) == 2
    assert main(["fuel", "--rate", "20", "--time", "51", "--fuel", "17"]) == 2


def test_cli_convert(capsys):
    assert main(["convert", "speed", "100", "--from", "kt", "--to", "kmh"]) == 0
    assert "185.2" in capsys.readouterr().out


def test_cli_navlog(tmp_path, capsys):
    legs = [
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
    path = tmp_path / "legs.json"
    path.write_text(json.dumps(legs), encoding="utf-8")
    assert main(["navlog", str(path)]) == 0
    out = capsys.readouterr().out
    assert "Alpha to Bravo" in out
    assert "TOTAL" in out


def test_cli_missing_subcommand_exits_2():
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_cli_bad_value_exits_1():
    assert main(["wind", "--course", "180", "--tas", "50", "--wind-from", "270", "--wind-speed", "60"]) == 1
