# e6b

[![CI](https://github.com/sajidkabir/e6b/actions/workflows/ci.yml/badge.svg)](https://github.com/sajidkabir/e6b/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)

An E6B flight computer in Python: the whiz wheel as a library and a
command line tool. Wind triangle, crosswind, time-speed-distance,
fuel, unit conversions, and multi-leg navlogs. Pure standard
library, no dependencies, installable from this repo.

The E6B is still the backup every VFR student is taught and every
exam still allows: when the GPS quits, the wind triangle and the
slide rule are what get you home. Web E6Bs and phone apps exist, but
there is no pip-installable Python E6B with a CLI, a tested wind
triangle in both directions, and a navlog builder. The Python E6B
repos on GitHub are small scripts (0 to 2 stars, no packaging, no
CLI, no test suite). This package fills that gap, and it is built
to be scripted: feed it a JSON leg list, get a navlog back, or call
one function from a larger flight-planning pipeline.

```text
$ e6b wind --course 90 --tas 125 --wind-from 230 --wind-speed 18
Course 90 deg, TAS 125 kt, wind 230/18 kt
Fly heading 95 deg (WCA +5 deg) for ground speed 138 kt
Headwind -14 kt, crosswind +12 kt (positive crosswind is from the right)
```

## Install

```bash
git clone https://github.com/sajidkabir/e6b.git
cd e6b
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Use

Wind triangle, both directions:

```bash
e6b wind --course 180 --tas 120 --wind-from 270 --wind-speed 12
e6b solve-wind --course 180 --heading 160 --tas 140 --gs 120
e6b track --heading 95 --tas 125 --wind-from 230 --wind-speed 18
e6b crosswind --runway 180 --wind-from 270 --wind-speed 15
```

Time, speed, distance, and fuel (give exactly two of the three for
tsd, and one of time or fuel for fuel):

```bash
e6b tsd --distance 300 --gs 190
e6b tsd --gs 190 --time 94.7
e6b fuel --rate 20 --time 51
e6b fuel --rate 20 --fuel 17
```

Conversions and navlogs:

```bash
e6b convert speed 100 --from kt --to kmh
e6b convert distance 80 --from km --to nm
e6b navlog examples/legs.json
```

Or from Python:

```python
import json

from e6b import wind_correction, compute_navlog, navlog_from_json

solution = wind_correction(course_deg=90, tas=125, wind_from_deg=230, wind_speed=18)
print(solution.heading_deg)     # about 95
print(solution.ground_speed)    # about 138

legs = navlog_from_json(json.load(open("examples/legs.json")))
result = compute_navlog(legs)
print(result.total_time_min, result.total_fuel_gal)
```

## Conventions (read this before trusting a sign)

- Bearings are degrees clockwise from true north, 0 to 360.
- Wind direction is the direction the wind comes FROM, as in METARs
  and winds-aloft forecasts.
- Headwind is positive against the course; a negative headwind is a
  tailwind of the same size.
- Crosswind is positive from the right of the course or runway,
  negative from the left.
- Wind correction angle is positive to the right: heading equals
  course plus WCA.
- Magnetic variation is east-positive: magnetic heading equals true
  heading minus east variation.

## What it computes

- Wind: heading and ground speed for a course, track and ground
  speed for a heading flown, and the reverse problem (recover the
  wind from course, heading, TAS, and ground speed).
- Runway wind: headwind and crosswind components for any runway
  heading.
- Slide rule: time, distance, and ground speed (any two give the
  third), fuel used, endurance, and fuel for a leg.
- Conversions: speed (kt, kmh, mph, ms), distance (nm, km, sm, m),
  volume (US gallons, litres), and fuel weight by pounds per gallon.
- Navlogs: a JSON leg list becomes per-leg headings, ground speeds,
  times, and fuel, with totals and a plain-text table.

## Verified against textbook problems

- Course 180, TAS 120, wind 270/12: heading 186, ground speed 119
  (published WCA 6 deg right, heading 186, GS 119).
- Course 090, TAS 125, wind 230/18: heading 095, ground speed 138
  (published heading 095, GS 138).
- Course 180, heading 160, TAS 140, GS 120: wind 104/49 (published
  wind 104/50, rounded).
- Every wind solution round-trips: feeding the solved heading back
  through the track function returns the original course and ground
  speed exactly.

## Honest scope

- This package takes true airspeed as an input. It does not convert
  calibrated or indicated airspeed to TAS; that conversion lives in
  isa-aero, and it is on this package's roadmap.
- Fuel weight defaults to avgas at 6.0 lb per US gallon. Jet A is
  about 6.7 to 6.8; pass your aircraft manual's figure.
- A crosswind component stronger than TAS has no heading that holds
  the course, so the function raises ValueError instead of
  returning a heading. The same honesty applies to zero ground
  speeds, negative fuel, and other meaningless inputs.
- This is a planning aid, not a certified flight computer. Check the
  numbers against your aircraft manual and the physical E6B before
  flying on them.
