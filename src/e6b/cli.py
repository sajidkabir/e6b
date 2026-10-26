"""Command line interface: e6b wind, crosswind, solve-wind, track,
tsd, fuel, convert, and navlog. Every subcommand prints plain numbers
a pilot can check against the physical whiz wheel, and exits with
status 2 (argparse) or 1 (a bad value) on bad input.
"""

import argparse
import json
import sys

from e6b.navlog import compute_navlog, navlog_from_json, navlog_table
from e6b.tsd import (
    distance_nm,
    endurance_min,
    format_duration,
    fuel_used_gal,
    ground_speed_kt,
    time_min,
)
from e6b.units import convert_distance, convert_speed, convert_volume
from e6b.wind import (
    ground_vector,
    normalize_angle,
    solve_wind,
    wind_components,
    wind_correction,
)


def _wind_parser(sub):
    parser = sub.add_parser("wind", help="heading and ground speed for a course")
    parser.add_argument("--course", type=float, required=True, help="true course, degrees")
    parser.add_argument("--tas", type=float, required=True, help="true airspeed, knots")
    parser.add_argument("--wind-from", type=float, required=True, help="wind from direction, degrees")
    parser.add_argument("--wind-speed", type=float, required=True, help="wind speed, knots")
    return parser


def _crosswind_parser(sub):
    parser = sub.add_parser("crosswind", help="headwind and crosswind for a runway")
    parser.add_argument("--runway", type=float, required=True, help="runway heading, degrees")
    parser.add_argument("--wind-from", type=float, required=True, help="wind from direction, degrees")
    parser.add_argument("--wind-speed", type=float, required=True, help="wind speed, knots")
    return parser


def _solve_wind_parser(sub):
    parser = sub.add_parser("solve-wind", help="recover the wind from a flown triangle")
    parser.add_argument("--course", type=float, required=True, help="true course held, degrees")
    parser.add_argument("--heading", type=float, required=True, help="true heading flown, degrees")
    parser.add_argument("--tas", type=float, required=True, help="true airspeed, knots")
    parser.add_argument("--gs", type=float, required=True, help="observed ground speed, knots")
    return parser


def _track_parser(sub):
    parser = sub.add_parser("track", help="track and ground speed for a heading flown")
    parser.add_argument("--heading", type=float, required=True, help="true heading, degrees")
    parser.add_argument("--tas", type=float, required=True, help="true airspeed, knots")
    parser.add_argument("--wind-from", type=float, required=True, help="wind from direction, degrees")
    parser.add_argument("--wind-speed", type=float, required=True, help="wind speed, knots")
    return parser


def _tsd_parser(sub):
    parser = sub.add_parser("tsd", help="solve one of time, distance, ground speed")
    parser.add_argument("--distance", type=float, help="distance, nautical miles")
    parser.add_argument("--gs", type=float, help="ground speed, knots")
    parser.add_argument("--time", type=float, help="time, minutes")
    return parser


def _fuel_parser(sub):
    parser = sub.add_parser("fuel", help="fuel used, or endurance for a fuel quantity")
    parser.add_argument("--rate", type=float, required=True, help="burn rate, gallons per hour")
    parser.add_argument("--time", type=float, help="time, minutes")
    parser.add_argument("--fuel", type=float, help="fuel quantity, gallons")
    return parser


def _convert_parser(sub):
    parser = sub.add_parser("convert", help="convert a speed, distance, or volume")
    parser.add_argument("kind", choices=["speed", "distance", "volume"])
    parser.add_argument("value", type=float)
    parser.add_argument("--from", dest="from_unit", required=True, help="source unit")
    parser.add_argument("--to", dest="to_unit", required=True, help="target unit")
    return parser


def _navlog_parser(sub):
    parser = sub.add_parser("navlog", help="compute a navlog from a JSON leg list")
    parser.add_argument("file", help="JSON file with a list of legs")
    return parser


def build_parser():
    parser = argparse.ArgumentParser(prog="e6b", description="E6B flight computer")
    sub = parser.add_subparsers(dest="command", required=True)
    _wind_parser(sub)
    _crosswind_parser(sub)
    _solve_wind_parser(sub)
    _track_parser(sub)
    _tsd_parser(sub)
    _fuel_parser(sub)
    _convert_parser(sub)
    _navlog_parser(sub)
    return parser


def _run(args):
    if args.command == "wind":
        solution = wind_correction(args.course, args.tas, args.wind_from, args.wind_speed)
        print("Course %.0f deg, TAS %.0f kt, wind %.0f/%.0f kt" % (solution.course_deg, solution.tas, solution.wind_from_deg, solution.wind_speed))
        print("Fly heading %.0f deg (WCA %+.0f deg) for ground speed %.0f kt" % (solution.heading_deg, solution.wca_deg, solution.ground_speed))
        print("Headwind %+.0f kt, crosswind %+.0f kt (positive crosswind is from the right)" % (solution.headwind, solution.crosswind))
    elif args.command == "crosswind":
        headwind, crosswind = wind_components(args.runway, args.wind_from, args.wind_speed)
        print("Runway %.0f, wind %.0f/%.0f: headwind %+.0f kt, crosswind %+.0f kt" % (normalize_angle(args.runway), normalize_angle(args.wind_from), args.wind_speed, headwind, crosswind))
        print("Positive crosswind is from the right, negative from the left.")
    elif args.command == "solve-wind":
        wind_from, wind_speed = solve_wind(args.course, args.heading, args.tas, args.gs)
        print("Wind %.0f/%.0f kt" % (wind_from, wind_speed))
    elif args.command == "track":
        track, gs = ground_vector(args.heading, args.tas, args.wind_from, args.wind_speed)
        print("Track %.0f deg, ground speed %.0f kt" % (track, gs))
    elif args.command == "tsd":
        given = [name for name, value in (("distance", args.distance), ("gs", args.gs), ("time", args.time)) if value is not None]
        if len(given) != 2:
            print("tsd needs exactly two of --distance, --gs, --time", file=sys.stderr)
            return 2
        if args.time is None:
            minutes = time_min(args.distance, args.gs)
            print("Time %s (%.1f minutes)" % (format_duration(minutes), minutes))
        elif args.distance is None:
            print("Distance %.1f nm" % distance_nm(args.gs, args.time))
        else:
            print("Ground speed %.1f kt" % ground_speed_kt(args.distance, args.time))
    elif args.command == "fuel":
        if (args.time is None) == (args.fuel is None):
            print("fuel needs exactly one of --time or --fuel, plus --rate", file=sys.stderr)
            return 2
        if args.time is not None:
            print("Fuel %.1f gal" % fuel_used_gal(args.rate, args.time))
        else:
            minutes = endurance_min(args.fuel, args.rate)
            print("Endurance %s (%.1f minutes)" % (format_duration(minutes), minutes))
    elif args.command == "convert":
        if args.kind == "speed":
            value = convert_speed(args.value, args.from_unit, args.to_unit)
        elif args.kind == "distance":
            value = convert_distance(args.value, args.from_unit, args.to_unit)
        else:
            value = convert_volume(args.value, args.from_unit, args.to_unit)
        print("%.4g %s" % (value, args.to_unit))
    elif args.command == "navlog":
        with open(args.file, encoding="utf-8") as handle:
            data = json.load(handle)
        result = compute_navlog(navlog_from_json(data))
        print(navlog_table(result))
    return 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    except OSError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
