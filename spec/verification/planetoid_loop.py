#!/usr/bin/env python3
"""
Verification: planetoid vibration → crystal toss → shatter loop.

Reference: 05-ai.md "Planetoid behavior", 02-entities.md "Planetoids".
Constants used (all from tunables.yaml#planetoid):
  vibration_max               (RchMax)   = 96
  vibration_damp_per_frame    (VibDamp)  = 2
  missile_vibration_add       (MisVib)   = 16
  crystal_toss_threshold      (CrProb)   = 16  (THRESHOLD, not probability)
  crystal_toss_damping        (CryDamp)  = 10  (not directly modeled here)

Verified mechanic (FALS/N1ALL.ASM:402-457 TOSCRYS):
  excess = vibration - crystal_toss_threshold
  if excess > 0 and rand_byte() <= excess:
      toss crystal
      vibration /= 2          # toss halves vibration

Earlier drafts modeled toss as a flat 16/255 chance per frame; that
was wrong. The correct mechanic is threshold-then-proportional, which
gives planetoids a meaningful "tipping point" feel.

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
    cry_threshold = t[("planetoid", "crystal_toss_threshold")]

    random.seed(seed)
    vibration = 0
    crystals_tossed = 0
    shattered = False
    missiles_fired = 0
    next_missile_frame = 0

    print(f"Planetoid simulation (seed={seed})")
    print(f"  RchMax={rch_max}, VibDamp={damp}, MisVib={mis_vib}, "
          f"CrProb_threshold={cry_threshold}")
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

        # Crystal toss: threshold-then-proportional (FALS/N1ALL.ASM:410-416).
        # excess = vibration - crystal_toss_threshold
        # if excess > 0 and rand_byte() <= excess: toss + halve vibration
        excess = vibration - cry_threshold
        if excess > 0 and random.randint(0, 255) <= excess:
            crystals_tossed += 1
            vibration //= 2  # halved on successful toss
            events.append(f"crystal tossed (#{crystals_tossed}) — vib halved")

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
    print("--- Slow fire (every 30 frames): below threshold, no tosses ---")
    print("    Demonstrates threshold-gated mechanic: vibration damps faster")
    print("    than slow fire can build it past CrProb=16.")
    simulate(seed=42, missile_interval=30, missile_count=8)
    print()
    print("--- Light attack (3 missiles, spaced 60 frames) ---")
    simulate(seed=42, missile_interval=60, missile_count=3, max_frames=300)
    print()
    print("--- Rapid fire (every 6 frames): crosses threshold, cascades crystals ---")
    print("    Demonstrates that sustained fire builds vibration past")
    print("    threshold, producing the 'tipping point' that yields crystals.")
    simulate(seed=42, missile_interval=6, missile_count=10, max_frames=200)


if __name__ == "__main__":
    main()
