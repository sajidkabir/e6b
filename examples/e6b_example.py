"""Demonstrate the e6b API on textbook wind problems and a navlog."""

import json
from pathlib import Path

from e6b import compute_navlog, navlog_from_json, navlog_table, wind_correction

# Textbook problem 1: course 180, TAS 120, wind 270/12.
solution = wind_correction(180, 120, 270, 12)
print("Course 180, TAS 120, wind 270/12:")
print("  Heading %.0f deg (WCA %+.0f deg), ground speed %.0f kt" % (solution.heading_deg, solution.wca_deg, solution.ground_speed))
print()

# Textbook problem 2: course 090, TAS 125, wind 230/18.
solution = wind_correction(90, 125, 230, 18)
print("Course 090, TAS 125, wind 230/18:")
print("  Heading %.0f deg (WCA %+.0f deg), ground speed %.0f kt" % (solution.heading_deg, solution.wca_deg, solution.ground_speed))
print()

# Navlog from the bundled JSON leg list.
legs_path = Path(__file__).with_suffix("").parent / "legs.json"
result = compute_navlog(navlog_from_json(json.loads(legs_path.read_text(encoding="utf-8"))))
print(navlog_table(result))
print()
print("Total time %.1f minutes, total fuel %.1f gal" % (result.total_time_min, result.total_fuel_gal))
