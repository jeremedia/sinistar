# Verification Log

This document records the second-pass verification of the spec against the
original 1983 ROM source. Each finding is one of:

- **Confirmed** — spec was correct as written
- **Corrected** — spec value or behavior was wrong; fixed in this pass
- **Added** — behavior present in source that was missing from the spec

The changes are reflected in the YAML data files and prose chapters.

## Files re-read directly during verification

- `WITT/COLLISIO.ASM` — every collision pair, scoring, special cases
- `WITT/SUBPART.ASM`, `SAM/ADDPIEC.ASM` — Sinistar piece economy
- `SAM/SAMTABLE.ASM` (PIECETB / ALIVE / PIECEND) — assembly / HP arithmetic
- `WITT/AIMWARR.ASM`, `WITT/WARRIOR.ASM`, `WITT/TABLES.ASM` (sqloffsets)
- `WITT/WORKER.ASM`, `WITT/THINK.ASM`
- `SAM/NEWTUNE.ASM`, `SAM/SAMTABLE.ASM` (Q* tune entries)
- `SAM/ADDSCOR.ASM` (BCD scoring math)
- `SAM/INITALL.ASM`, `MICA/HSTDIM.ASM`, `SAM/TB13.ASM` (CMOS init / DEFALT table)
- `WITT/CHASE.ASM`, `WITT/VELOCITY.ASM` — speed-table consumer semantics
- `SAM/FUNCTION.ASM` — `asrd0`–`asrd5` definitions

## Findings

### 1. Sinistar HP — **Corrected**

**Spec said:** `pieces_required: 4` sinibomb hits.

**Truth:** **12 sinibomb hits** to destroy a fully-assembled Sinistar.

The piece table (`SAM/SAMTABLE.ASM:533`) has 20 entries: 12 skull/body
pieces between `PIECETB` and the `ALIVE` marker, then 8 facial pieces
(JAWR through NEZ) between `ALIVE` and `PIECEND`. During assembly,
workers deliver 20 crystals → `PIECEPT` advances from `PIECETB` to
`PIECEND`, then resets to the `ALIVE` marker. From the alive state,
each sinibomb hit moves `PIECEPT` back one slot toward `PIECETB`
(`WITT/SUBPART.ASM:62` → `SAM/ADDPIEC.ASM:25`). Reaching `PIECETB`
triggers the death sequence (+15,000 points).

Only the 12 body pieces are individually destructible. The 8 facial
pieces are visual-only once assembled; they are not "armor", they
simply aren't iterated by `SUBPIEC`. They do disappear when the death
sequence fires.

Updated:
- `tunables.yaml#sinistar.pieces_required: 12`
- `tunables.yaml#sinistar.assembly_pieces: 20` (now confirmed, with note)
- `02-entities.md`, `05-ai.md` — narrative corrected
- `entities.yaml#sinistar.hp_or_pieces: 12`

### 2. Sinistar stun on hit — **Added**

Each sinibomb hit increments an `InStun` timer by 2 frames
(`WITT/COLLISIO.ASM:407-409`). While stunned, Sinistar's velocity is
also halved (`WITT/SUBPART.ASM:74-85`). This is an important readability
mechanic — the player can see the boss flinch.

Added to `tunables.yaml#sinistar.stun_per_hit_frames: 2` and `05-ai.md`.

### 3. Player shots do NOT collect crystals — **Corrected**

**Spec said:** player_shot × crystal → crystal collected.

**Truth:** the `CRYSTAL × PLSHOT` pair is **pass-through**
(`WITT/COLLISIO.ASM:226`, in the commented "pass-through" list). Only
direct ship contact collects a crystal (`PLAYER × CRYSTAL` →
`AddBomb` + addscore $200, `WITT/COLLISIO.ASM:141-148`).

Updated:
- `03-physics-collision.md` collision matrix — removed false row
- `02-entities.md` Player Shot description — corrected
- `entities.yaml#player_shot` description — corrected

### 4. Crystal-worker caller-match logic — **Added**

A worker passes through any crystal that did not "call" it. Only the
specific crystal whose `OScWCr` references this worker gets picked up
(`WITT/COLLISIO.ASM:276-287`). This prevents workers from snatching
random nearby crystals — they only collect the one assigned to them.

This is a non-obvious design detail that affects tactical play (the
player can sometimes intercept a tossed crystal even when a worker is
nearby, if that worker isn't bound to it).

Added to `05-ai.md` Worker section.

### 5. Bomb-bay-full crystal pickup — **Added**

When the player collides with a crystal while holding `MAXBOMBS = 20`
sinibombs, the crystal is still consumed but no bomb is added. The
game plays a different tune (`QFulCr`, priority 21) and displays the
message "CRYSTAL SAVED FOR WARP ENGINES" (`WITT/COLLISIO.ASM:160-188`).

This is a charming detail — the message reassures the player that the
"wasted" crystal will pay off later.

Added:
- `sfx.yaml#crystal_saved_for_warp` event (replacing speculative `thrust`)
- `04-player.md` and `02-entities.md` Crystal section

### 6. Sinibomb has no AOE radius — **Corrected**

**Spec said:** sinibomb detonation clears nearby workers/warriors.

**Truth:** A sinibomb collides with exactly one target at a time
(`WITT/COLLISIO.ASM:336-411`). Each `SBOMB × {WORKER, WORKCR, WARRIOR,
PLANET, SINI, WASHOT}` pair kills both the bomb and the target — no
splash damage. There is no AOE code path.

The "panic clear" intuition I had was wrong. The bomb is powerful
because (a) it homes, (b) it's the only thing that hurts Sinistar, and
(c) on Sinistar contact it does damage *and* stuns. Not because of AOE.

Updated:
- `02-entities.md` Sinibomb section — removed AOE description
- `03-physics-collision.md` — removed AOE paragraph

### 7. 5-warrior squadron formation angles — **Corrected**

**Spec said:** `formation_angle_5_ship: [128, 128, 128, 128]`.

**Truth (`WITT/TABLES.ASM:172-175`):** `[128, 64, 128, 64]` (where 64
is the assembler's workaround for the original signed `-(circle*12/16)
= -192 ≡ 64 (mod 256)`).

The other formation angles (2/3/4-ship) confirmed correct.

Updated `tunables.yaml#warrior.formation_angle_5_ship`.

### 8. Worker AI mission count — **Corrected**

**Spec said:** 6 worker missions: DRIFT, TAIL, INTERCEPT, MINE,
DELIVER_CRYSTAL, EVADE.

**Truth (`WITT/WORKER.ASM:75-92`):** **5 missions**:
DRIFT, TAIL, INTERCEPT, DELIVER_CRYSTAL, EVADE. There is no separate
MINE mission for workers — workers TAIL planetoids when mining (the
TAIL mission is "orbit any caller", and a planetoid can be the caller).

Updated `05-ai.md` Worker section.

### 9. Acceleration routine semantics inverted — **Corrected**

**Spec said:** `asrd0` = instant, `asrd1` = slowest (1/128 per frame),
`asrd5` = snappiest non-instant (1/8 per frame).

**Truth (`SAM/FUNCTION.ASM:289-313`):** `asrdN` shifts D right by `N`
bits. The output is added to the current velocity to close the gap
toward target. So:

| routine | shifts | gap closed per frame |
|---------|--------|----------------------|
| `asrd0` | 0      | full gap (instant)   |
| `asrd1` | 1      | gap / 2              |
| `asrd2` | 2      | gap / 4              |
| `asrd3` | 3      | gap / 8              |
| `asrd4` | 4      | gap / 16             |
| `asrd5` | 5      | gap / 32             |

`asrd1` is **the snappiest** non-instant routine; `asrd5` is **the
slowest**. The inverted description was wrong.

Updated `speed-tables.yaml#unit_notes.accel_routine_meaning` and
`03-physics-collision.md`.

### 10. Difficulty default — **Corrected**

**Spec said:** `difficulty_of_play.default: 3` (best guess).

**Truth (`SAM/TB13.ASM:74`):** Factory default is **5** (the maximum).

Note: `SAM/TB13.ASM:71-88` is the canonical CMOS factory defaults
table (`DEFALT`). Reading it cleared up several other unknowns.

Updated `operator-defaults.yaml`.

### 11. Player starting ships — **Confirmed and added**

**Spec said:** "verify against MICA/HSTDIM.ASM".

**Truth (`SAM/TB13.ASM:73`):** SHIPS PER GAME = `$03` = 3 ships.

Added explicit `operator-defaults.yaml#ships_per_game.default: 3`.

### 12. Continuous Fire setting — **Added**

`SAM/TB13.ASM:75` defines a CMOS field "CONTINUOUS FIRE" with default
`$01` (enabled). When enabled, holding the fire button auto-fires;
when disabled, each shot requires a button press.

Added to `operator-defaults.yaml`.

### 13. Coinage default values — **Added**

`SAM/TB13.ASM:76-83` exposes the coinage internals as discrete CMOS fields:

| field   | default | meaning |
|---------|---------|---------|
| CSELCT  | `$03`   | coin select mode |
| SLOT1M  | `$01`   | slot 1 multiplier |
| SLOT2M  | `$04`   | slot 2 multiplier |
| SLOT3M  | `$01`   | slot 3 multiplier |
| CUNITC  | `$01`   | coin unit count |
| CUNITB  | `$00`   | coin unit base |
| MINUNT  | `$00`   | minimum units before credit |

Added to `operator-defaults.yaml#settings.coinage.subfields` for
completeness. A modern remake can ignore these in favor of free-play.

### 14. SFX priorities — **Confirmed**

I cross-checked every Q* entry in `SAM/SAMTABLE.ASM:340-466`. All
priorities I had recorded match within the priority field (`_IPRIO`,
1–63). One entry (`QFulCr`, priority 21, defined inline in
`WITT/COLLISIO.ASM:182-188`) was missing from the spec; added in
finding #5.

The `warrior_alert` and `thrust` entries I had were **speculative** —
no `Qwalert` or `Qthrust` exists in the source. Removed `thrust`;
removed `warrior_alert` (no source).

### 15. SFX duration semantics — **Clarified**

Tune entries can have multiple `_PRIO`/`_TIME` segments. The total
duration is the sum of all `_TIME` values until `_STOP`. My spec had
some single-segment durations; I updated multi-segment entries to
reflect total tune length.

### 16. Speed table lookup — **Confirmed with addendum**

The lookup walks rows largest-distance-first; the first row where
`current_distance >= row.distance` matches (`WITT/VELOCITY.ASM:36-39`).
The verification YAML's row ordering is correct. Added an explanatory
note to `speed-tables.yaml#unit_notes`.

### 17. Speed table units — **Clarified**

The `speed` field is a 16-bit signed value in scanner-velocity units
(scanner-pixels per Task16-tick ≈ 16 frames). The `subd SLVEL` step in
`WITT/VELOCITY.ASM:99,134` confirms units are scanner-pixels.

The conversion to a modern engine: treat `speed` as a relative tunable.
The shapes of the curves (especially the non-monotonic Sinistar chase)
matter more than absolute units.

### 18. Scoring — **Confirmed**

All score values match prose:

| event | hex BCD | decimal |
|-------|---------|---------|
| Sinistar destroyed | `$7000+$8000` | 15,000 |
| Sinistar piece destroyed | `$500` | 500 |
| Warrior killed (any) | `$500` | 500 |
| Worker killed (any) | `$150` | 150 |
| Crystal collected | `$200` | 200 |
| Warrior shot intercepted | `$100` | 100 |

The Sinistar-destroyed score is split into two BCD addscore calls
(`$7000` then `$8000`) because the BCD adder maxes at 4 BCD digits.

### 19. PreBoY (pre-bounce-Y) — **Added**

`WITT/COLLISIO.ASM:299` defines `PreBoY` — when Sinistar is alive but
the player collides during warp, the bounce path is taken. Generally
when planet ↔ {object} collide, the planet routes through `PreBou`
which adds vibration before the bounce, then `PosBou` after. This
means **collision with a planetoid adds vibration** (in addition to
direct missile hits).

Added to `05-ai.md` Planetoid section.

## Summary

- **8 corrections** (HP, formation, asrd, difficulty, AOE, player-shot crystal,
  worker missions, sfx speculation)
- **6 additions** (stun, caller-match, bay-full, ships, continuous fire,
  coinage subfields, planet-bounce vibration)
- **5 confirmations** (formation 2/3/4, all SFX priorities checked, scoring,
  speed-table semantics, speed-table lookup direction)

The spec is materially more accurate after this pass. The verification
scripts in `verification/*.py` continue to pass; the formation script
output now reflects the corrected 5-ship angles.

## Third-pass corrections (post external code review)

An external review caught regressions and a deeper mechanical miss. All
findings confirmed and fixed.

### 20. Prose chapters lagged YAML edits — **Corrected**

In the second pass I updated YAML data files but missed two narrative
mentions in `02-entities.md`:

- The Player Shot section still claimed shots collect crystals.
- The Sinibomb section still claimed bombs clear nearby workers/warriors.

Both contradicted the corrected collision matrix in `03-physics-collision.md`
and entries in `entities.yaml`. A reader following the spec's recommended
"30-minute read" path (`00`, `02`, `05`, `10`) would have implemented
wrong mechanics. Fixed in `02-entities.md`.

### 21. Glossary stale — **Corrected**

`12-glossary.md` Piece entry still said `pieces_required = 4` after the
second pass corrected it to 12. Fixed.

### 22. Planetoid crystal toss is threshold-then-proportional, **NOT** flat — **Corrected** (load-bearing)

**Spec said:** flat 16/255 ≈ 6.3% per-frame chance to toss while vibrating.

**Truth (`FALS/N1ALL.ASM:402-457`, TOSCRYS routine):**

```
A = OSRcht (current vibration)
A = A - CrProb        ; CrProb = 16 is a THRESHOLD, not a probability
if A <= 0: skip
random_byte = rand()
if random_byte > A: skip
toss crystal
vibration /= 2        ; (lsra) — vibration HALVED on successful toss
```

So `CrProb = 16` is a threshold the vibration must exceed, and the toss
probability is `(vibration - 16) / 256` — proportional to the *excess*
vibration above threshold. Examples:

| vibration | excess | toss prob /frame |
|-----------|--------|------------------|
| 16        | 0      | 0%               |
| 32        | 16     | ~6%              |
| 64        | 48     | ~19%             |
| 80        | 64     | ~25%             |
| 96 (max)  | 80     | ~31%             |

This gives planetoids a meaningful "tipping point" feel — light hits
toss nothing; heavy hits cascade crystals. Plus the post-toss vibration
halving means tosses self-limit (a planetoid won't dump all its crystals
in one frame).

The flat-probability model in my earlier draft would have under-tossed
crystals near max vibration and over-tossed at low vibration —
materially wrong for the crystal economy.

Updated:
- `tunables.yaml#planetoid.crystal_toss_threshold: 16` (renamed from
  `crystal_toss_probability`, with explanatory note linking to the old name)
- `tunables.yaml#planetoid.crystal_toss_vibration_decay: 2` (new — vibration halves on toss)
- `02-entities.md` Planetoid section
- `05-ai.md` Planetoid loop pseudocode
- `verification/planetoid_loop.py` rewritten to use the correct logic

### 23. Planetoids award NO score — **Corrected** (load-bearing)

**Spec said:** 5 points per planetoid destroyed.

**Truth:** **0 points.** Verified by reading every planetoid kill path:

- `WITT/COLLISIO.ASM:337-349` (SBOMB,PLANET): calls `QBang` and
  `OKiVec` twice (kill bomb, kill planet), no `addscore`.
- `FALS/N1ALL.ASM:519-533` (KRPl1..KRPl5): each calls `KilVib` then
  `KilNorm` and returns. No `addscore`.

The "5 points" entry in my spec came from a comment block in
`COLLISIO.ASM:31-37`:

```
;*      15,000 Sinistar skull
;*         500 Sinistar skeleton piece
;*         500 Warriors
;*         200 Crystals
;*         150 Workers
;*         100 Warrior shot
;*           5 Planetoids (including Pluto) (handled by KRPlan?)
```

Note the trailing `(handled by KRPlan?)` — even the original author
hedged. The answer is "no, KRPl* don't award points". I trusted the
comment instead of grepping for `addscore` calls. The reviewer's
instinct to follow the call sites was the right verification approach.

Updated:
- `entities.yaml`: all five planetoid types `score_value: 0`
- `scoring.yaml#destroy_planetoid.points: 0` with a note explaining the
  comment-vs-code mismatch
- `07-scoring.md` summary table and design note

### 24. Verification scripts not reproducible without PyYAML — **Corrected**

The scripts import `yaml` but the repo had no `requirements.txt` or
install instructions. Added:

- `spec/verification/requirements.txt` with `PyYAML>=6.0`
- Updated `spec/verification/README.md` with `pip install` step

### 25. WASHODDS provenance path wrong — **Corrected**

`populations.yaml#difficulty.source` cited `FALS/WASHODDS.ASM`. The
file in the repo is `WITT/WASHODDS.ASM` (Rich Witt's module — the WAgg
warrior aggression code lives in WITT, not FALS). Fixed.

## Why these slipped past pass 2

Three patterns worth naming so the next reviewer can be fast:

1. **YAML/prose drift.** I updated YAML records but didn't grep prose
   for narrative mentions of the same concept. The fix is to either
   centralize values (and have prose reference them) or to grep prose
   for every changed YAML key. The coverage check confirms references
   resolve, but doesn't catch wrong claims that don't reference YAML.
2. **Trusting comments over call sites.** The "5 points planetoids"
   error was reading a header comment block, not the actual score
   calls. For score values, the only authoritative source is `addscore`
   call sites. Same for behavior — the only authoritative source is
   the routine being called.
3. **Surface-skimming load-bearing routines.** I read `FALS/N1.ASM` and
   `FALS/N1SYM.ASM` for population tables but not `FALS/N1ALL.ASM` for
   the actual TOSCRYS routine. The "All" suffix should have been a
   tell that this file aggregates the gameplay loops.

## Fourth-pass corrections (second external review)

A second external review caught regressions and finer-grained mechanical
errors. All findings confirmed and fixed.

### 26. Score-value `000` regression — **Corrected**

**Spec said:** `entities.yaml#sinistar_piece.score_value: 000` and
`#warrior.score_value: 000` (parsed as 0).

**Truth:** both should be 500. Verified `WITT/COLLISIO.ASM:432` (warrior
kill via player shot, `ldd #$500`) and `:375` (warrior kill via sinibomb,
`ldd #$500`) and `:62` (Sinistar piece score in SUBPART, `ldd #$500`).
Also `scoring.yaml` correctly says 500 — entities.yaml was the only file
out of sync.

**Cause:** when fixing the planetoid score (5 → 0) I used
`replace_all: true` on `score_value: 5`, which mangled both `score_value:
500` instances (sinistar_piece line 42, warrior line 82) into
`score_value: 000`. Targeted replacement is the right tool here; bulk
replacement on numeric values is dangerous.

Fixed both back to 500.

### 27. Planetoid bounce vibration claim — **Corrected** (load-bearing)

**Spec said:** any object bouncing off a planetoid contributes Richter
vibration via `PreBou` / `PosBou`. Implementers would have generated
crystals from collisions that should not mine the rock.

**Truth (`FALS/N1ALL.ASM:55-90`):** `PreBou` and `PosBou` only manipulate
the vibration *velocity* (`OSLVib`/`OSSVib`) — they subtract it before a
bounce so the bounce math operates on translation alone, then add it back
after. Neither routine touches the Richter scale (`OSRcht`).

The Richter scale is incremented only via the `AddVib` routine
(`FALS/N1ALL.ASM:98`). `AddVib` is called from exactly three collision
sites (`WITT/COLLISIO.ASM`):

- Line 326-328: PLANET ↔ SINI bounce
- Line 330-333: PLANET ↔ PlShot or PLANET ↔ WaShot

That's it. Ordinary bounces between a planetoid and a worker, warrior,
crystal, or player do **not** add Richter.

The "Vib. Bounce" annotation in the original COLLISIO.ASM source (which
I had read as "vibration-adding bounce") actually means "bounce that has
to handle existing vibration via PreBou/PosBou" — not "bounce that adds
vibration."

Updated `03-physics-collision.md` collision matrix and `05-ai.md`
planetoid loop pseudocode to reflect this. The rule is now: **only
shots and Sinistar contact add Richter to a planetoid.**

### 28. AddVib increment is mass-dependent, not flat — **Corrected**

**Spec said:** `missile_vibration_add: 16` per shot (a flat constant).

**Truth (`FALS/N1ALL.ASM:98-136`):** AddVib computes the increment from
the *planet's* pseudo-mass (`OSPers`) via the `InvTbl` reciprocal-mass
lookup, then right-shifted by 2:

```
B = planet_pseudo_mass / 16      ; clamped to >= 1
increment = InvTbl[B] >> 2
```

With `InvTbl[N] ≈ 100/N`, this gives:

| planet type | mass | increment |
|-------------|------|-----------|
| 3           | 20   | ~25       |
| 1           | 60   | ~8        |
| 2 / 4       | 50   | ~6        |
| 5           | 90   | ~5        |

Lighter planetoids vibrate more easily — a meaningful design choice that
my flat-16 model would have erased.

The constant `MisVib = 16` is defined in `FALS/N1SYM.ASM:16` but **never
referenced anywhere else in the codebase**. It's a dead/legacy constant.
The real value used by the running code is the InvTbl-based computation.

Renamed `tunables.yaml#missile_vibration_add` to
`#vibration_add_per_shot_intended` and documented the actual formula.

### 29. Triggering paths for Richter add — **Clarified**

**Spec said:** "missile/sinibomb impact" adds vibration to a planet.

**Truth:** Only player_shot and warrior_shot impacts add vibration
(`WITT/COLLISIO.ASM:330-333`). Sinibomb on a planetoid does not — it
kills the planet outright (`COLLISIO.ASM:337-349` SBOMB,PLANET path,
which calls `OKiVec` for both bomb and planet, no `AddVib`).

Updated `02-entities.md` and `05-ai.md`.

### 30. Vibrate ordering — **Corrected**

**Spec said:** damp first, then roll for crystal toss.

**Truth (`FALS/N1ALL.ASM:194-225`):** the `Vibrate` Task4 cycle has
three stages with sleeps between them. At the end of stage 3:

1. `TosCrys` — try to toss a crystal (line 211)
2. `VibStp` — stop vibration motion (line 213)
3. **Then** damp Richter by `VibDamp` (line 223-225)

So toss check happens **before** damping. This matters because the
toss probability is computed against the *pre-damp* vibration value.
Updated `verification/planetoid_loop.py` and `05-ai.md` pseudocode.

### 31. Stale MINE / crystal_toss_probability references — **Corrected**

**Spec said:** in the worker decision tree at `05-ai.md:41`, mission
transitions to `MINE` when close. The same chapter explicitly states
workers have no MINE mission. And `:53` referenced the removed
`crystal_toss_probability` constant by name.

Both fixed. The worker decision tree now says `INTERCEPT(target) → TAIL
once close`, and the crystal-toss reference now points to
`crystal_toss_threshold`.

The Warrior MINE state at line 95 is correct and remains — warriors
*do* have a mine mission (`WITT/WARRIOR.ASM:113-117`); only workers
don't.

## Why these slipped past pass 3

- **`replace_all: true` is a footgun** for substrings of larger numbers.
  I should have used targeted edits with line numbers, or a sed-style
  pattern that anchors the value (`^score_value: 5$`).
- **The "Vib. Bounce" comment in COLLISIO.ASM misled me** into thinking
  every planet collision added Richter. Following the call graph
  (PreBou/PosBou actually do what?) was the right move and the reviewer
  did exactly that.
- **I extracted `MisVib = 16`** from the symbol file without confirming
  it was actually referenced. Symbol-defined constants need to be checked
  against `grep` to confirm they're live.
- **Multi-pass narrative drift**: "MINE when close" survived earlier
  edits because removing the worker MINE mission was done as a localized
  table edit; the decision-tree pseudocode wasn't grep'd for the term.
  This is the same class of regression as pass 3's review caught.


## What still needs verification

These remain "needs_research" or "best-effort" in the YAML:

- Operator difficulty range — confirmed default 5, but the upper bound
  (5? 9? something else?) needs verification against the diag ROM,
  which is out of spec scope. **Pragma:** treat as 1–5 in the remake.
- Operator message length cap — would require tracing `MICA/ATTMSGS.ASM`.
- Several tune-table durations are sums of multi-segment `_TIME` values;
  if a tune ends early via priority pre-emption, effective duration is
  shorter. The YAML records *maximum* durations.
- The `BargraphEnable` / `WittRock` / debug-utilities code paths are
  out of canon scope but contain unused-but-interesting design
  fragments. Not extracted.

## Fifth-pass — automating drift prevention (post-review)

After the reviewer caught stale narrative numerics for a *second* time
(finding #32, stale "4 sinibomb hits" prose in two chapters), the
review-then-fix loop was clearly not catching the same class of error.
Two-and-a-half reviews to find every stale prose number is too many.

Added `verification/numeric_drift_check.py`:

- For each load-bearing concept (Sinistar HP, scoring values, bay
  capacity, tick rate, extra-ship thresholds, vibration constants,
  Sinistar stun, warrior cooldown), defines a `(label, regex, yaml_ref)`
  triple.
- Scans every prose chapter for matches of the regex outside fenced
  code blocks.
- Requires the corresponding `yaml_ref` to appear within ±12 lines
  of each match.
- Reports any unresolved match as a violation.
- Supports per-chapter exemptions for legitimate historical references
  (e.g., "originally $05 in SAM/DEFAULT.SRC", "≥4 needed in the
  original [attract demo]").

Running this against the post-review spec surfaced 24 bare numeric
claims that had no nearby YAML citation; all were updated to cite the
appropriate `data/*.yaml#id`. The tool now exits clean.

The verification README documents a recommended pre-commit pair:

```sh
python3 verification/coverage_check.py && \
python3 verification/numeric_drift_check.py
```

These two together enforce both directions of the invariant: every
prose YAML reference resolves to a record, and every numeric claim
in prose either cites a YAML record or is explicitly exempt.

This is the structural fix for the regression class that took out
findings #20, #23, #26, and #32. The next pass should not see another
stale narrative numeric — and if it does, that finding can be added
as a new regex to the drift check so it can never recur silently.

## Fourth-pass final consistency corrections (reviewer follow-up)

Two additional regressions caught by the reviewer after the consolidated
fourth pass above. These are the residual stale-prose findings that
weren't visible from the YAML coverage check.

### 32. Progression/game-flow stale "4 hits" prose — **Corrected**

The second and third passes corrected Sinistar HP to **12 sinibomb hits**
for a fully-assembled Sinistar in the YAML and most prose, but two
gameplay-flow references still said 4 hits:

- `06-progression.md` sector advance and pacing text.
- `08-game-flow.md` gameplay termination bullet.

Both now reference the source-backed `tunables.yaml#pieces_required = 12`
body-piece counter and avoid reintroducing the old 4-hit prototype value.

Same class of regression as finding #26 (score_value 000) and finding #20
(player_shot collects crystals prose): YAML was updated, narrative
chapters were not grep'd for the same concepts. The coverage check
confirms references resolve but doesn't catch wrong claims that don't
cite YAML — those need a textual sweep.

### 33. score_value `000` regression — already covered in #26

(Duplicate of finding #26 above. Both surfaced the same regression.
The reviewer's independent catch is recorded here for traceability.)
