# Verification

This folder contains exercises that re-derive specific gameplay behaviors
**using only the spec and YAML data** — no consultation of the original
asm. The exercises serve as evidence that the spec is sufficient to
implement Sinistar 2026.

## Files

- [`VERIFICATION_LOG.md`](VERIFICATION_LOG.md) — second-pass verification
  log: corrections and additions made to the spec after re-reading the
  load-bearing asm files (`COLLISIO`, `SUBPART`, `ADDPIEC`, `WARRIOR`,
  `WORKER`, `TABLES`, `NEWTUNE`, `SAMTABLE`, `TB13`, `FUNCTION`,
  `VELOCITY`). Read this first to understand what changed and why.
- [`coverage_check.py`](coverage_check.py) — walks every prose chapter
  and confirms each `data/*.yaml#id` reference resolves. Run with
  `python3 verification/coverage_check.py` from `spec/`.
- [`warrior_formation.py`](warrior_formation.py) — derives a 4-warrior
  squadron's positions around a leader using only `tunables.yaml`
  formation angles. Verifies the spec's geometry math.
- [`planetoid_loop.py`](planetoid_loop.py) — simulates a planetoid being
  shot, vibrating, ejecting crystals, and shattering, using only
  `tunables.yaml` constants. Verifies the spec describes the full
  vibration → toss → shatter loop.
- [`sinistar_chase.py`](sinistar_chase.py) — uses
  `speed-tables.yaml#stbl_sinistar_chase` to simulate Sinistar
  approaching the player at varying distances. Verifies the
  non-monotonic chase curve produces the expected "winding up" feel.

## What success looks like

Each script produces a textual trace of the simulated behavior. A reader
can compare that trace to the asm behavior (mentally, or by inspection of
`WITT/AIMWARR.ASM`, `FALS/N1.ASM`, and `WITT/STBLSINI.ASM`) and decide
whether the spec captures enough to reproduce the behavior.

If a script reveals a behavior the spec doesn't describe (a missing
constant, an undocumented branch), that's a spec gap to fix.

## Running

```sh
cd spec
python3 verification/coverage_check.py
python3 verification/warrior_formation.py
python3 verification/planetoid_loop.py
python3 verification/sinistar_chase.py
```

All scripts are pure Python 3 with `pyyaml` as the only dependency.
