# Changelog

All notable changes to this project are documented here. The format
follows [Keep a Changelog](https://keepachangelog.com/), and versions
follow [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-26

### Added

- Wind triangle in both directions: `wind_correction` (heading and
  ground speed for a course) and `solve_wind` (recover the wind from a
  flown course, heading, TAS, and ground speed), plus `ground_vector`
  for the track a heading actually produces.
- Crosswind and headwind components with a stated sign convention:
  headwind positive against the course, crosswind positive from the
  right. Magnetic variation helpers (`to_magnetic`, `to_true`).
- Time-speed-distance solver, fuel used and endurance, and fuel for a
  leg, with a plain duration formatter.
- Unit conversions: speed (kt, kmh, mph, ms), distance (nm, km, sm,
  m), volume (US gallons, litres), and fuel weight by
  pounds-per-gallon (avgas default 6.0).
- Multi-leg navlogs: JSON leg lists, per-leg heading, ground speed,
  time, and fuel, plus totals and a plain-text table.
- CLI `e6b` with subcommands wind, crosswind, solve-wind, track,
  tsd, fuel, convert, and navlog.
- Test suite of 46 checks, including textbook wind problems with
  published answers, round trips, and input validation.
- Example script and example navlog JSON.

## Roadmap

- CAS to TAS from pressure altitude and temperature (currently lives
  in isa-aero; this package takes TAS as an input and says so).
- Wind aloft interpolation for multi-altitude navlogs.
- Holding pattern entry and descent planning helpers.
