#!/usr/bin/env python3
"""
Verification: warrior squadron formation geometry.

Using only tunables.yaml's formation_angle_N_ship constants, derive the
positions of N-1 wing followers around a leader for N = 2, 3, 4, 5.

Reference: 05-ai.md "Squadron formation".
Constants: tunables.yaml#formation_angle_2_ship .. #formation_angle_5_ship
Unit: CIRCLE=256 (so 128 = 180°, 192 = 270°).
"""

import math
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TUNABLES = os.path.join(os.path.dirname(HERE), "data", "tunables.yaml")

ORBIT_RADIUS_PX = 80.0  # arbitrary visual radius; the *angles* are what we verify


def load_formation_angles():
    with open(TUNABLES) as fh:
        doc = yaml.safe_load(fh)
    out = {}
    for entry in doc["tunables"]["warrior"]:
        if entry["name"].startswith("formation_angle_"):
            n = int(entry["name"].split("_")[2].split("_")[0])  # "2_ship" → 2
            out[n] = entry["value"]
    return out


def circle256_to_radians(t):
    return (t / 256.0) * 2 * math.pi


def derive_positions(squad_size, leader_xy, leader_heading_circle256, angles):
    """Place leader, then followers at the given offset angles."""
    lx, ly = leader_xy
    leader_heading_rad = circle256_to_radians(leader_heading_circle256)
    positions = [("leader", lx, ly)]
    for i, off in enumerate(angles):
        wing_angle = leader_heading_rad + circle256_to_radians(off)
        fx = lx + ORBIT_RADIUS_PX * math.cos(wing_angle)
        fy = ly + ORBIT_RADIUS_PX * math.sin(wing_angle)
        positions.append((f"wing{i+1}", fx, fy))
    return positions


def main():
    angles_by_size = load_formation_angles()
    leader = (0.0, 0.0)
    heading = 0  # facing +x

    print("Warrior squadron formation derivation")
    print("=====================================")
    print(f"Leader at {leader}, heading {heading}/256 ({heading/256*360:.0f}°)")
    print(f"Visual orbit radius: {ORBIT_RADIUS_PX:.0f}px (illustrative)")
    print()

    for size in sorted(angles_by_size):
        offsets = angles_by_size[size]
        print(f"--- {size}-ship squadron ---")
        print(f"  follower offsets (CIRCLE=256): {offsets}")
        print(f"  follower offsets (degrees):    {[f'{o/256*360:.0f}°' for o in offsets]}")
        positions = derive_positions(size, leader, heading, offsets)
        for label, x, y in positions:
            print(f"    {label:8s}  ({x:7.1f}, {y:7.1f})")
        print()


if __name__ == "__main__":
    main()
