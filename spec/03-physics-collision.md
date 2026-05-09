# 03 — Physics and Collisions

## Movement model

Every entity has a 2D position and a 2D velocity stored with **sub-pixel
fractional precision**. Each simulation tick:

```
position += velocity * dt
```

where `dt = 1/60 s` for the original and may be different for a remake's
fixed-step rate (recommended: still 60Hz). Sub-pixel precision matters because
slow entities (e.g., a worker drifting at fractional pixels per frame) would
otherwise quantize to zero velocity.

## Acceleration

Each entity's velocity is updated by an **acceleration profile** chosen from a
small set of routines (`asrd0`–`asrd5` in `speed-tables.yaml`). The profiles
correspond to ease-toward-target curves of varying snappiness:

- `asrd0`: instant — velocity snaps to target
- `asrd1`: slowest — barely closes 1/128 of the gap per frame
- `asrd5`: snappiest non-instant — closes 1/8 of the gap per frame

For each AI entity, the chosen speed table (e.g., `stbl_warrior_intercept`)
gives a *target* speed for the current distance to target; the row's `accel`
field tells the entity how fast to ease toward that speed.

A modern remake can use any reasonable easing curve. The naming convention is
preserved here purely as a vocabulary for the speed tables.

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

| pair                              | behavior                                                  |
|----------------------------------- |----------------------------------------------------------- |
| player_ship × worker / warrior     | bounce + damage to player (lose ship, dying state)         |
| player_ship × planetoid            | bounce (player takes no damage; ship can be wedged)        |
| player_ship × crystal              | crystal collected (200 pts, +1 sinibomb), no bounce        |
| player_ship × sinistar (alive)     | bite — player dies; Sinistar continues                     |
| player_shot × worker               | worker dies (150 pts); shot consumed                       |
| player_shot × warrior              | warrior dies (500 pts); shot consumed                      |
| player_shot × warrior_shot         | both consumed (100 pts)                                    |
| player_shot × sinistar_piece       | piece destroyed (500 pts); shot consumed                   |
| player_shot × planetoid            | planetoid takes vibration; shot consumed                   |
| player_shot × sinistar             | shot consumed; **no damage** to Sinistar                   |
| player_shot × crystal              | crystal collected (200 pts, +1 sinibomb); shot consumed    |
| sinibomb × sinistar                | Sinistar takes 1/4 damage; sinibomb consumed; AOE blast    |
| sinibomb × worker / warrior        | enemy dies (150 / 500 pts); sinibomb consumed              |
| sinibomb × planetoid               | planetoid takes large vibration; sinibomb consumed         |
| warrior_shot × player_ship         | player dies (no bounce, no points)                         |
| worker × planetoid (mining state)  | mine — extracts crystal, no bounce                         |
| worker × sinistar (delivering)     | crystal delivered, assembly +1                             |
| object × object (same kind)        | bounce (workers off workers, crystals off crystals, etc.) |
| fragment × anything                | no collision (visual particle only)                        |

This table is the canon. The original implements it via a 16-bit collision-
mask per type indexed by a `CLTABLE`; a remake can use any pair-keyed
data structure.

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

## Sinibomb area-of-effect

When a sinibomb detonates (on Sinistar contact, on auto-detonate near
Sinistar, or on impact with another enemy), **all on-screen and nearby
off-screen workers and warriors in a small radius** are destroyed. This is
the "panic clear" behavior — sinibombs are powerful, which is why the
crystal economy gates them.

The exact radius is implementation-tunable; the *behavior contract* is:
"a sinibomb detonation should clear the immediate threats around its impact
point and is the dominant tool for breaking up swarming attacks."

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
