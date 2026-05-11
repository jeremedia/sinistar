#!/usr/bin/env python3
"""
Verification: planetoid vibration → crystal toss → shatter loop.

Reference: 05-ai.md "Planetoid behavior", 02-entities.md "Planetoids".

Verified mechanics (FALS/N1ALL.ASM):
  Vibrate task (lines 194-249) — Task4-scheduled, 3-stage shake cycle:
    stage 1: VibNew (start shake);   Sleep
    stage 2: VibRev (reverse shake); Sleep
    stage 3: TosCrys (line 211 — check toss FIRST)
             VibStp  (stop vibration motion)
             vibration -= VibDamp   (damping happens AFTER toss check)
             if vibration >= RchMax: shatter

  TosCrys (lines 402-457):
    excess = vibration - CrProb       # CrProb=16 is THRESHOLD, not probability
    if excess > 0 and rand_byte() <= excess:
        toss crystal
        vibration /= 2                # halved on successful toss (lsra)

  AddVib (lines 98-136) — increment is MASS-DEPENDENT:
    increment = InvTbl[planet_mass / 16, clamped to 1] >> 2
    Called by Planet × {PlShot, WaShot} and Planet × SINI bounces only.
    SBOMB × PLANET kills the planet outright (no vibration).
    Ordinary bounces (worker/warrior/crystal/player × planet) use
    PreBou/PosBou which manage vibration *velocity*, not Richter.

Earlier drafts had three errors corrected here:
  1. Toss check ordered AFTER damp (wrong — toss happens first).
  2. Flat 16/255 toss probability (wrong — threshold-then-proportional).
  3. Flat MisVib=16 increment (wrong — mass-dependent via InvTbl).

Simulates a Type 1 planetoid (mass 60) hit by player shots.
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


def add_vib_increment(planet_mass):
    """Richter increment from AddVib (FALS/N1ALL.ASM:98-136).

    increment = InvTbl[planet_mass / 16, clamped to 1] >> 2
    InvTbl[N] approximates 100/N (256-entry reciprocal-mass lookup).
    Heavier planets gain LESS Richter per hit.
    """
    mass_idx = max(1, planet_mass // 16)
    inv_mass = 100 // mass_idx
    return inv_mass >> 2


def simulate(seed=42, planet_mass=60, hit_interval=30, hit_count=8,
             max_frames=400):
    t = load_tunables()
    rch_max = t[("planetoid", "vibration_max")]
    damp = t[("planetoid", "vibration_damp_per_frame")]
    cry_threshold = t[("planetoid", "crystal_toss_threshold")]
    increment = add_vib_increment(planet_mass)

    random.seed(seed)
    vibration = 0
    crystals_tossed = 0
    shattered = False
    missiles_fired = 0
    next_missile_frame = 0

    print(f"Planetoid simulation (seed={seed}, planet_mass={planet_mass})")
    print(f"  RchMax={rch_max}, VibDamp={damp}, "
          f"AddVib increment={increment} (mass-derived), "
          f"CrProb_threshold={cry_threshold}")
    print(f"  Firing {hit_count} player shots, one every {hit_interval} frames")
    print()
    print(f"  frame  vib  events")
    print(f"  -----  ---  ------")

    # The original Vibrate task (FALS/N1ALL.ASM:194-225) does:
    #   stage 1: VibIni / VibNew / sleep
    #   stage 2: VibIni / VibRev / sleep
    #   stage 3: VibIni / TosCrys / VibStp / damp Richter
    # i.e. toss check happens BEFORE damping at the end of each shake cycle.
    # We approximate one full shake cycle per frame here for clarity.

    for f in range(max_frames):
        events = []

        # Missile impact (player_shot or warrior_shot path) → AddVib.
        # NOTE: AddVib's increment is computed from planet pseudo-mass via
        # InvTbl in the original (FALS/N1ALL.ASM:98-136). For this simplified
        # demo we use a single mis_vib value; a faithful sim should derive
        # the increment per planetoid type.
        if missiles_fired < hit_count and f == next_missile_frame:
            vibration = min(rch_max, vibration + increment)
            missiles_fired += 1
            next_missile_frame = f + hit_interval
            events.append(f"shot {missiles_fired}/{hit_count} hit (+{increment})")

        # The real Vibrate task runs on Task4 (~once every 4 frames), with
        # toss + damp happening at the end of each 3-stage shake cycle.
        # Approximate by running the cycle every 4 frames.
        if f % 4 == 0:
            # 1. Crystal toss: threshold-then-proportional (FALS/N1ALL.ASM:410-416)
            excess = vibration - cry_threshold
            if excess > 0 and random.randint(0, 255) <= excess:
                crystals_tossed += 1
                vibration //= 2  # halved on successful toss
                events.append(f"crystal tossed (#{crystals_tossed}) — vib halved")

            # 2. Damp Richter (FALS/N1ALL.ASM:223-225)
            vibration = max(0, vibration - damp)

        # 3. Shatter check
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
    print("Mass-dependent AddVib increments:")
    for label, m in [("Type 3 (mass 20, lightest)", 20),
                     ("Type 2/4 (mass 50)", 50),
                     ("Type 1 (mass 60)", 60),
                     ("Type 5 (mass 90, heaviest)", 90)]:
        print(f"  {label:30s} → +{add_vib_increment(m)} Richter/hit")
    print()
    print("--- Type 1 planet, slow fire (every 30 frames) ---")
    print("    Heavy planet + slow fire: vibration stays below threshold.")
    simulate(seed=42, planet_mass=60, hit_interval=30, hit_count=8)
    print()
    print("--- Type 1 planet, rapid fire (every 6 frames) ---")
    print("    Sustained fire crosses threshold, tossing crystals.")
    simulate(seed=42, planet_mass=60, hit_interval=6, hit_count=10, max_frames=200)
    print()
    print("--- Type 3 (light) planet, slow fire (every 30 frames) ---")
    print("    Light planets vibrate much more easily — same fire pattern,")
    print("    different outcome.")
    simulate(seed=42, planet_mass=20, hit_interval=30, hit_count=8)


if __name__ == "__main__":
    main()
