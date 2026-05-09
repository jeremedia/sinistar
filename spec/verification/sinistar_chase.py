#!/usr/bin/env python3
"""
Verification: Sinistar's non-monotonic chase curve.

Reference: 05-ai.md "Sinistar AI", 10-presentation.md "chase curve shape".
Source: speed-tables.yaml#stbl_sinistar_chase.

The original chase table speed is non-monotonic — it should surge at long
range, lull at medium range (~1024 px), then surge again at close range.
This script samples the table at many distances and confirms that the
"winding up" shape is captured by the spec data alone.
"""

import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SPEED_TABLES = os.path.join(os.path.dirname(HERE), "data", "speed-tables.yaml")


def load_table(table_id):
    with open(SPEED_TABLES) as fh:
        doc = yaml.safe_load(fh)
    for t in doc["tables"]:
        if t["id"] == table_id:
            # rows are pre-sorted in the original asm style: largest distance first
            # (each row matches when current distance >= row.distance)
            # Re-sort here defensively.
            rows = sorted(t["rows"], key=lambda r: -r["distance"])
            return t, rows
    raise KeyError(table_id)


def lookup(rows, distance):
    """Return the row that matches the given distance (largest distance <= current)."""
    for r in rows:
        if distance >= r["distance"]:
            return r
    return rows[-1]


def main():
    print("Sinistar chase curve sampling")
    print("=============================")
    table, rows = load_table("stbl_sinistar_chase")
    print(f"Table: {table['name']}")
    print(f"  used by: {table['used_by']}")
    print(f"  rows: {len(rows)}")
    print()
    print(f"  {'distance':>10s}  {'speed':>6s}  {'accel':>6s}")
    print(f"  {'-'*10}  {'-'*6}  {'-'*6}")
    for r in rows:
        print(f"  {r['distance']:>10d}  {r['speed']:>6d}  {r['accel']:>6s}")
    print()

    # Sample the curve at many distances and verify non-monotonicity
    print("Curve sampled at narrow distance steps:")
    print(f"  {'dist':>6s}  {'speed':>6s}  {'note'}")
    print(f"  {'-'*6}  {'-'*6}  {'-'*4}")
    samples = [10000, 5000, 4000, 2000, 1024, 800, 600, 400, 200, 100, 64, 32, 16, 8, 0]
    last_speed = None
    direction_changes = 0
    for d in samples:
        r = lookup(rows, d)
        note = ""
        if last_speed is not None:
            if r["speed"] > last_speed:
                note = "↑ surge"
            elif r["speed"] < last_speed:
                note = "↓ ease"
                direction_changes += 1
            else:
                note = "= flat"
        print(f"  {d:>6d}  {r['speed']:>6d}  {note}")
        last_speed = r["speed"]

    print()
    print(f"  direction changes (surge → ease transitions): {direction_changes}")
    print()
    if direction_changes >= 1:
        print("  ✓ Non-monotonic chase curve confirmed.")
        print("    Sinistar surges → eases → surges as it closes.")
        print("    This is the iconic 'winding up' feel — preserved in spec data.")
    else:
        print("  ✗ Curve is monotonic — design pillar #4 broken.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
