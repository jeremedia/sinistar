# 02 — Entities

The full entity catalog with stats lives in `data/entities.yaml`. This chapter
describes each entity's *role*, *visual identity guidelines*, and *state machine*.
For numeric stats (mass, score, sprite size), reference the YAML.

## Player Ship

**Role:** the player. Single ship, momentum-based control, primary fire and sinibomb release.

**Visual identity:** Modern art is open. The ship should have a clear *facing direction* (the player's heading), be visually distinct from all enemies, and read clearly on screen even surrounded by debris. The 1983 original was a small triangular craft.

**State machine:**

```
   spawn ──► alive ─────────► dying ──► (despawn)
              │                  ▲
              │                  │
              └─► warping ───────┘
                  (Sinistar killed)
```

- **alive**: takes input, fires, collides with enemies and crystals
- **dying**: explosion sequence, no input, sound plays, no collisions; spawns fragments
- **warping**: post-Sinistar-kill exit animation; player accelerates off-screen (`tunables.yaml#warp_velocity`); transitions to next sector spawn

See `04-player.md` for input, firing, and lives detail.

## Sinistar

**Role:** the boss. The game's central threat and namesake. Assembled over time from crystals delivered by workers; once complete, it hunts and bites the player. The only weapon that damages it is the sinibomb.

**Visual identity:** The original is a giant skull-planet — eyes, jaw, teeth, fearsome silhouette. Modern art is open, but the entity must read as **enormous**, **angry**, and **mouth-forward** (because biting is its attack). The mouth must animate with speech (lipsync — see `tunables.yaml#lipsync_offset` for the original's solution to making the mouth not collide with itself).

**State machine:**

```
   absent ──► assembling ──► alive ──► dying ──► (sector ends)
                  ▲             │
                  │             │
                  └─────────────┘
                  (assembly progress visible)
```

- **absent**: not yet on map (early in a sector); pieces are being delivered
- **assembling**: visible but incomplete; partial collision; cannot bite; speaks `i_am_sinistar`
- **alive**: fully assembled; chases player; speaks aggressive lines (`beware_i_live`, `run_coward`, etc.); can bite; takes 12 sinibomb hits to kill (`tunables.yaml#pieces_required`). Each sinibomb hit destroys one body piece, awards 500 points, and stuns Sinistar for `tunables.yaml#stun_per_hit_frames = 2` frames (and halves its current velocity).
- **dying**: shatter animation; no collision; cleared from sector

**Approach behavior:** Sinistar's chase uses the table `speed-tables.yaml#stbl_sinistar_chase`. The curve is *non-monotonic* — speed rises, drops at medium range (~1024px), then rises sharply at close range. This is the iconic "winding up" feel; preserve the curve shape.

**Orbit shrink:** While approaching, Sinistar's orbit factor decreases from `tunables.yaml#max_orbit_radius = 12` by 1 per frame. On-screen orbit shrink continues until 3/4 of max; below that, shrinking continues only while off-screen. This produces visible advance-and-pause behavior.

**Lipsync offset:** During speech, an internal offset (`tunables.yaml#lipsync_offset = 412`) is applied to distance calculations so that the animating mouth does not register collisions with itself. A remake using a modern collision system can simply exclude the mouth bone from collision; this offset is a 6809 implementation artifact.

## Sinistar Piece (skull fragment)

**Role:** an individual skull piece in transit. Workers carry pieces toward Sinistar; if the player shoots one in transit, they score 500 and the piece is destroyed (assembly delayed slightly).

**Visual identity:** A small chunk of the Sinistar's silhouette — recognizable as belonging to it. The original used pre-rendered skull-segment sprites.

**State:** stateless projectile-like; carried by a worker until delivered or destroyed.

## Worker

**Role:** the crystal-economy enemy. Mines crystals from planetoids and delivers them to Sinistar, advancing assembly. Slow, lightly armored, easy to kill — but they are *the clock*. Killing workers is how the player buys time.

**Visual identity:** Small drone-like unit. Distinct from warriors (different silhouette, no weapons). The variant carrying a crystal should be *visibly carrying it* (animation/glow/attached crystal sprite) so the player can prioritize.

**Mission states (AI):** `DRIFT`, `TAIL`, `INTERCEPT`, `DELIVER_CRYSTAL`, `EVADE`. See `05-ai.md`.

**Crystal handoff:** When a worker delivers a crystal to Sinistar (within `tunables.yaml#crystal_delivery_tolerance = 4 pixels` of the mouth), the crystal is consumed, Sinistar's assembly progresses, and the worker reverts to `DRIFT`. If the worker is killed while carrying, the crystal drops as a free-floating crystal the player can collect.

## Warrior

**Role:** the combat enemy. Aggressive, fires aimed shots, flies in formations. Warriors do not advance Sinistar's assembly; they exist to kill the player.

**Visual identity:** Larger, more menacing silhouette than workers. Visibly armed. The original used a craft sprite with a turret.

**Formation behavior:** Warriors fly in squadrons of 1–5. Squadron formation uses fixed wing-offset angles around the leader (`tunables.yaml#formation_angle_2_ship` through `#formation_angle_5_ship`, in CIRCLE=256 degree units). This produces the classic "fighter wing closing on the player" choreography.

**Shooting inhibitor:** Each warrior has a per-shot cooldown (`tunables.yaml#shooting_inhibitor_max = 15 frames`) that **only counts down while the warrior is on-screen and within scroll bounds**. Off-screen warriors do not advance their cooldown. This prevents off-screen barrages and keeps combat readable.

## Warrior Shot

**Role:** projectile fired by warriors at the player. Travels in a straight line. Can be intercepted by player shots (100 points).

**Visual identity:** Small, fast, distinct from player shots in color/shape.

## Player Shot

**Role:** player primary fire. Travels in the direction the ship is facing (or the joystick direction at fire-time). Hits warriors (+500), workers (+150), warrior shots (+100), and Sinistar pieces in transit (+500); adds vibration to planetoids. Does **NOT** collect crystals (pass-through) and does **NOT** damage Sinistar (pass-through). See `03-physics-collision.md` for the full collision matrix.

**Visual identity:** Fast projectile, distinct from warrior shots. Multiple may be on-screen.

## Sinibomb

**Role:** the only weapon that kills Sinistar. Player launches one; it homes in on Sinistar. Each Sinistar contact destroys one body piece (`scoring.yaml#destroy_sinistar_piece`), stuns Sinistar for `tunables.yaml#stun_per_hit_frames` frames, and consumes the bomb. Worker / warrior / planetoid contacts also kill the bomb and the target. **No area-of-effect** — each sinibomb collides with exactly one target. The player carries up to `tunables.yaml#max_in_bay = 20` sinibombs; each crystal collected via direct ship contact adds one.

**Visual identity:** Larger than a player shot, slower, visibly homing. Should be readable as "this is the answer to Sinistar."

**Behavior:** Once launched, follows `speed-tables.yaml#stbl_sinibomb` (direct homing) or `#stbl_sinibomb_orbit` (indirect approach) depending on geometry. Auto-detonates if the player drops it off-screen and both axis distances to Sinistar fall below `tunables.yaml#detonation_distance = 80 pixels`.

## Crystal

**Role:** the dual-purpose collectible. Workers carry crystals toward Sinistar (bad for player); the player collects them for sinibomb ammo (good for player) and 200 points. Free-floating crystals come from planetoid impacts (vibration-induced ejection).

**Visual identity:** Small, glowing, valuable-looking. Should pulse or flash gently to draw attention (see `sfx.yaml#crystal_flash`).

**Lifespan:** A free-floating crystal exists for `tunables.yaml#crystal_max_age = 10 seconds` before despawning (`sfx.yaml#crystal_flash` plays as ambient pulsation while it's available).

## Planetoids (5 types)

**Role:** environmental hazards and crystal sources. Planetoids drift. When struck (by player shots or sinibombs), they vibrate. Sufficient vibration ejects crystals. Maximum vibration shatters them into fragments.

**Visual identity:** Five distinct planetoid types varying in size and apparent mass. The original used different rock sprites; modern art is open. Larger types should *read* as heavier (slower to push, higher inertia in collisions).

**Vibration mechanic:** Each planetoid has a vibration "Richter" value, capped at `tunables.yaml#vibration_max = 96`. Vibration decays by `#vibration_damp_per_frame` per shake cycle.

Vibration is *added* only by these collisions (`FALS/N1ALL.ASM:98-136` AddVib):

- **player_shot or warrior_shot hits a planetoid** — `WITT/COLLISIO.ASM:330-333`
- **planetoid bounces against Sinistar** — `WITT/COLLISIO.ASM:326-328`

The increment is **mass-dependent**: lighter planetoids (type 3, mass 20) gain ~25 Richter per hit; heavier planetoids (type 5, mass 90) gain ~5. See `tunables.yaml#vibration_add_per_shot_intended` for the formula. Sinibombs do **not** add vibration to planetoids — `SBOMB × PLANET` kills the planetoid outright (`WITT/COLLISIO.ASM:337-349`). Ordinary bounces (worker/warrior/crystal/player vs. planetoid) do **not** add vibration either — they use `PreBou`/`PosBou` which only handle existing vibration velocity, not Richter.

Crystal-toss is *threshold-then-proportional*: tosses only happen when vibration exceeds `#crystal_toss_threshold = 16`, and probability per shake cycle is `(vibration − threshold) / 256` (so ~0% just above threshold, ~31% at max vibration). After a successful toss, vibration is halved (`#crystal_toss_vibration_decay`). At max vibration, the planetoid shatters.

## Fragment / Particle

**Role:** explosion debris. Inert visual particle that tumbles outward and decays. No collision interaction.

**Visual identity:** Small, fast-moving, with trail. The art should feel *catastrophic* when many fragments spawn at once (Sinistar shatter).

## State-machine cross-references

- Player state machine details: `04-player.md`
- Sinistar AI and assembly: `05-ai.md` (Sinistar section)
- Worker / Warrior AI decision trees: `05-ai.md`
- Planetoid vibration loop: `05-ai.md` (Planetoid section)
- Collision matrix and bounce rules: `03-physics-collision.md`
