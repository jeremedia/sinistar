# 03 — Physics and Collisions

## Movement model

Every entity has a 2D position and a 2D velocity stored with **sub-pixel
fractional precision**. Each simulation tick:

```
position += velocity * dt
```

where `dt = 1/60 s` for the original and may be different for a remake's
fixed-step rate (recommended: match `tunables.yaml#tick_rate_hz`, 60Hz).
Sub-pixel precision matters because
slow entities (e.g., a worker drifting at fractional pixels per frame) would
otherwise quantize to zero velocity.

## Acceleration

Each entity's velocity is updated by an **acceleration profile** chosen from a
small set of routines (`asrd0`–`asrd5`, defined in `SAM/FUNCTION.ASM:289-313`).
Each routine arithmetic-shifts the velocity gap right by N bits and adds the
result back to current velocity. So `asrdN` closes `1 / 2^N` of the gap per
frame:

| routine | shifts | gap closed per frame |
|---------|--------|----------------------|
| `asrd0` | 0      | full gap (instant)   |
| `asrd1` | 1      | gap / 2 (snappiest)  |
| `asrd2` | 2      | gap / 4              |
| `asrd3` | 3      | gap / 8              |
| `asrd4` | 4      | gap / 16             |
| `asrd5` | 5      | gap / 32 (slowest)   |

For each AI entity, the chosen speed table (e.g., `stbl_warrior_intercept`)
gives a *target* speed for the current distance to target; the row's `accel`
field tells the entity how fast to ease toward that speed.

A modern remake can use any reasonable easing curve. The naming convention is
preserved here purely as a vocabulary for the speed tables. Note that
`speed-tables.yaml#unit_notes.accel_routine_meaning` is the authoritative
reference.

## Elastic collisions (bounce)

When two physical entities collide and at least one pair entry in the
collision matrix says "bounce", the system performs a **mass-weighted elastic
bounce**:

```
# along each axis (x and y treated independently)
m1, m2 = mass(a), mass(b)
total  = m1 + m2
v1', v2' = (v1 * (m1 - m2) + 2 * m2 * v2) / total,
           (v2 * (m2 - m1) + 2 * m1 * v1) / total
```

The original uses an `INVTBL` reciprocal-mass lookup (256 entries of `100/X`)
for fast division. A modern remake can do the math directly.

Bounces consume one frame of "bounce flag" state on each entity (the original
sets bits 1–0 to track recent bounces) so the same pair doesn't re-resolve
inside the bounding box. A remake should de-duplicate using whatever its
collision system already provides (e.g., contact pair IDs).

The `bounce_collision` SFX (`sfx.yaml`) plays at priority 16 for 3 ticks.

## Collision matrix

Not every entity pair collides, and not every collision is a bounce. The pair
behavior is governed by a matrix:

The pair behavior matrix below is verified against `WITT/COLLISIO.ASM`.

**Bounces (mass-weighted elastic):**

Note: `PreBou` / `PosBou` (`FALS/N1ALL.ASM:59,77`) wrap each bounce that
involves a vibrating object. They subtract the vibration *velocity*
(`OSLVib` / `OSSVib`) before the bounce calculation and add it back
after, so the bounce math operates on translation only. They do **not**
modify the Richter scale (`OSRcht`). Only the explicit `AddVib` paths
below add Richter.

| pair                                  | notes                                       |
|--------------------------------------- |---------------------------------------------|
| player ↔ worker / worker_w_crystal     | bounce; disabled during warp                |
| player ↔ warrior                       | bounce; disabled during warp                |
| player ↔ planetoid                     | bounce only (no Richter added)              |
| player ↔ sinistar (assembling)         | bounce — Sinistar can't bite until ALIVE    |
| crystal ↔ crystal / worker_w_crystal / warrior | bounce                            |
| worker ↔ worker / worker_w_crystal / warrior  | bounce                             |
| worker_w_crystal ↔ worker_w_crystal / warrior | bounce                             |
| warrior ↔ warrior                      | bounce                                      |
| planet ↔ crystal / worker / worker_w_crystal / warrior | bounce only (no Richter added) |
| planet ↔ planet                        | bounce only (no Richter added either side)  |
| planet ↔ sinistar                      | bounce + planet `AddVib` (can shatter planet) |
| sinistar ↔ sinistar                    | bounce (rare; only in pathological states)  |

**Pickups, hits, and special:**

Numeric point values below are the authoritative spec for the listed
events; the corresponding YAML rows are
`scoring.yaml#collect_crystal` (player ↔ crystal),
`scoring.yaml#kill_worker` (worker kills),
`scoring.yaml#kill_warrior` (warrior kills),
`scoring.yaml#kill_warrior_shot` (warrior-shot intercepts),
`scoring.yaml#destroy_sinistar_piece` (sinibomb ↔ sinistar piece),
and `tunables.yaml#stun_per_hit_frames` (sinistar stun on hit).

| pair                                  | behavior                                       |
|--------------------------------------- |------------------------------------------------|
| player ↔ crystal                       | crystal consumed (+200 pts, +1 sinibomb to bay if not full; "CRYSTAL SAVED FOR WARP ENGINES" if full) |
| player ↔ sinistar (alive)              | SINIBITE — player dies; Sinistar speech queued |
| player ↔ warrior_shot                  | player dies; shot consumed                     |
| player_shot ↔ worker / worker_w_crystal | worker dies (+150 pts); shot consumed; if WORKCR, crystal is left behind |
| player_shot ↔ warrior                  | warrior dies (+500 pts); shot consumed         |
| player_shot ↔ warrior_shot             | both consumed (+100 pts)                       |
| player_shot ↔ planet                   | planet vibrates; shot consumed                 |
| warrior_shot ↔ worker / worker_w_crystal | worker dies; shot consumed (no points to player) |
| sinibomb ↔ sinistar                    | one body piece destroyed (+500 pts); planet vibrates; bomb consumed; Sinistar stunned (see `tunables.yaml#stun_per_hit_frames`) |
| sinibomb ↔ worker / worker_w_crystal   | worker dies (`scoring.yaml#kill_worker`, +150); bomb consumed; "SINIBOMB INTERCEPTED" message |
| sinibomb ↔ warrior                     | warrior dies (`scoring.yaml#kill_warrior`, +500); bomb consumed; "SINIBOMB INTERCEPTED" message |
| sinibomb ↔ planet                      | planet shattered; bomb consumed                |
| sinibomb ↔ warrior_shot                | both consumed                                  |
| crystal ↔ worker (caller-match only)   | if this crystal "called" this worker (OScWCr), crystal is given to worker; else PASS THROUGH |
| {warrior_shot, worker, worker_w_crystal, warrior} ↔ fragment | fragment dies; shot/object continues |

**Pass-through (explicit no-op):**

- `player ↔ sinibomb / player_shot / fragment`
- `sinibomb ↔ player_shot / sinibomb / crystal / fragment`
- `worker_w_crystal ↔ sinistar` (workers carrying crystals deliver via different path, not collision)
- `warrior ↔ warrior_shot`, `warrior_shot ↔ warrior_shot`
- `planet ↔ fragment`
- `crystal ↔ player_shot / warrior_shot / fragment` (player shots do **not** collect crystals)
- `sinistar ↔ player_shot / warrior_shot / fragment` (player shots do **not** damage Sinistar)
- `player_shot ↔ fragment`, `fragment ↔ fragment`

**Important corrections from earlier drafts:**

- Player shots do **not** collect crystals. Only ship contact does.
- Player shots do **not** damage Sinistar. Only sinibombs do.
- Sinibomb has **no AOE**. Each sinibomb collides with exactly one target.
- Crystal-worker pickup requires caller-match — workers don't pick up arbitrary nearby crystals.

The original implements this matrix via 16-bit collision masks per type
indexed by `CLTABLE` (`SAM/SAMTABLE.ASM:597`); a remake can use any
pair-keyed data structure.

## Pixel-precise collision

The original does a two-stage check: first a bounding-box pass, then a
pixel-overlap test (`SAM/PIXCHK.ASM`). The pixel test only fires when the
boxes overlap.

A modern remake should use convex shape collision (capsule / OBB / mesh)
appropriate to the entity. Pixel-precision *was* essential on a low-resolution
CRT — modern displays have enough resolution that good convex shapes are
visually equivalent.

## Sinistar bite

When Sinistar is in `alive` state, on-screen, and not dying (`SinGrave == 0`),
and the player ship is within Sinistar's mouth bounding region, the player
dies (`SINIBITE` collision). The mouth offset is given by
`tunables.yaml#mouth_offset_long / #mouth_offset_short`.

During player warp-out (post-Sinistar-kill, see `04-player.md`), all player
collisions are disabled.

## Sinibomb impact (no AOE)

Each sinibomb collides with exactly one target. There is no splash damage.
The sinibomb is powerful for three other reasons:

1. **It homes** on Sinistar (via `speed-tables.yaml#stbl_sinibomb`), so the
   player doesn't need to aim it.
2. **It is the only weapon that damages Sinistar.** Player shots pass through.
3. **On Sinistar contact**, it both destroys one body piece (+500 pts) and
   stuns Sinistar for `tunables.yaml#stun_per_hit_frames = 2` frames.

Because the bay holds at most `tunables.yaml#max_in_bay` (20) sinibombs and
each crystal grants only one, the crystal economy is the gate on sinibomb
usage. No AOE is needed for the bomb to feel powerful.

## Warp immunity

While the player is in `warping` state (after killing Sinistar, exiting the
sector), all collisions involving the player are disabled. The ship
accelerates off-screen at `tunables.yaml#warp_velocity` and the next sector
loads.

## Out-of-sector simulation

Off-screen entities continue updating. Off-screen workers can grab tossed
crystals probabilistically (`tunables.yaml#crystal_catch_probability`,
`#crystal_catch_distance`). Off-screen warriors do not advance their shooting
cooldown — this keeps off-screen warriors from accumulating shots they would
fire the moment they re-enter the screen.

## Modernization notes

- Mass-weighted elastic bounce is straightforward in any modern physics
  engine. Treat masses (`data/entities.yaml`) as canon ratios; absolute
  values can be scaled.
- The pixel-overlap collision check is hardware-era; any well-tuned convex
  shape collision is fine.
- The collision matrix is canon. A remake should expose it as data, not
  hard-coded `if` chains, so it's easy to verify and tune.
- Sub-pixel precision is essential for slow entities. Use floats / fixed-point
  with at least 8 fractional bits.
