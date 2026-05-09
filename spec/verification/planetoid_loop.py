#!/usr/bin/env python3
"""
Verification: planetoid vibration → crystal toss → shatter loop.

Reference: 05-ai.md "Planetoid behavior", 02-entities.md "Planetoids".
Constants used (all from tunables.yaml#planetoid):
  vibration_max               (RchMax)   = 96
  vibration_damp_per_frame    (VibDamp)  = 2
  missile_vibration_add       (MisVib)   = 16
  crystal_toss_probability    (CryProb)  = 16/255 ≈ 0.0627 per frame
  crystal_toss_damping        (CryDamp)  = 10  (not directly modeled here)

Plus tunables.yaml#sinibomb#max_in_bay (informational).

Simulates: an idle planetoid hit by missiles every 30 frames. Tracks
vibration, crystal tosses, and the shatter event.
"""

import os
import random
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TUNABLES = os.path.join(os.path.dirname(HERE), "data", "tunables.yaml")


def load_tunables():
    with open(TUNABLES) as fh:
        doc = yaml.safe_load(fh)
    out = {}
    for cat, entries in doc["tunables"].items():
        if isinstance(entries, list):
            for e in entries:
                out[(cat, e["name"])] = e["value"]
    return out


def simulate(seed=42, missile_interval=30, missile_count=8, max_frames=400):
    t = load_tunables()
    rch_max = t[("planetoid", "vibration_max")]
    damp = t[("planetoid", "vibration_damp_per_frame")]
    mis_vib = t[("planetoid", "missile_vibration_add")]
    cry_prob = t[("planetoid", "crystal_toss_probability")]  # 0.063

    random.seed(seed)
    vibration = 0
    crystals_tossed = 0
    shattered = False
    missiles_fired = 0
    next_missile_frame = 0

    print(f"Planetoid simulation (seed={seed})")
    print(f"  RchMax={rch_max}, VibDamp={damp}, MisVib={mis_vib}, CryProb={cry_prob:.3f}/frame")
    print(f"  Firing {missile_count} missiles, one every {missile_interval} frames")
    print()
    print(f"  frame  vib  events")
    print(f"  -----  ---  ------")

    for f in range(max_frames):
        events = []

        # Missile impact?
        if missiles_fired < missile_count and f == next_missile_frame:
            vibration = min(rch_max, vibration + mis_vib)
            missiles_fired += 1
            next_missile_frame = f + missile_interval
            events.append(f"missile {missiles_fired}/{missile_count} hit (+{mis_vib})")

        # Damping
        vibration = max(0, vibration - damp)

        # Crystal toss roll while vibrating
        if vibration > 0 and random.random() < cry_prob:
            crystals_tossed += 1
            events.append(f"crystal tossed (#{crystals_tossed})")

        # Shatter check
        if vibration >= rch_max and not shattered:
            shattered = True
            events.append("SHATTER")

        if events:
            print(f"  {f:5d}  {vibration:3d}  {'; '.join(events)}")

        if shattered:
            break

    print()
    print(f"  result:  vibration={vibration}, crystals={crystals_tossed}, "
          f"shattered={shattered}")
    return crystals_tossed, shattered


def main():
    print("Planetoid vibration / crystal toss / shatter loop")
    print("=" * 50)
    print()
    simulate(seed=42, missile_interval=30, missile_count=8)
    print()
    # Lighter attack — should not shatter, may still toss crystals
    print("--- Lighter attack: 3 missiles, spaced 60 frames ---")
    simulate(seed=42, missile_interval=60, missile_count=3, max_frames=300)


if __name__ == "__main__":
    main()
