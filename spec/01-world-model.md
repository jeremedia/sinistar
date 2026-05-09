# 01 — World Model

## Space

Sinistar takes place in an open 2D **sector** — a continuous play space larger than the screen. The player ship moves freely in any direction; the camera follows. There is no explicit map boundary the player collides with: the world wraps or extends beyond the visible area. Entities outside the visible viewport remain simulated (workers continue mining, warriors continue patrolling, Sinistar continues approaching) at reduced fidelity (e.g., off-screen workers grab crystals probabilistically — see `tunables.yaml#crystal_catch_probability`).

A **scanner** (radar) compresses the entire sector into a panel below the play area, showing entity positions relative to the player. The scanner is the player's only awareness of distant threats. The Sinistar's approach is announced first by speech, then by a scanner blip, then by its appearance on screen.

### Coordinates

The world uses a 2D Cartesian coordinate system. The original ROM names the axes `L` (long, horizontal) and `S` (short, vertical) — this naming is a 6809 implementation artifact and **a remake should use ordinary x/y**.

Internal positions are stored with sub-pixel fractional precision so that slow-moving entities accumulate motion correctly across frames.

### Scanner mapping

The scanner compresses world coordinates into scanner-cell coordinates with fixed scaling factors: roughly **24 world pixels per scanner cell horizontally** and **12 vertically** (`tunables.yaml#scanner_l_scale`, `#scanner_s_scale`). These specific numbers are hardware-constrained; a remake should pick scaling that fits its display while preserving the *function* — peripheral threat awareness with enough resolution to read direction but not enough to read precise position.

## Time

### Frame model

The original game runs at **60Hz** locked to the CRT vertical blanking interval (`tunables.yaml#tick_rate_hz`). Game logic, AI, and physics advance one tick per frame.

A modern remake should:

- Use a **fixed-step simulation at 60Hz** for game logic (so AI, physics, and scoring are deterministic and frame-rate-independent).
- Decouple rendering from simulation. Render at the display's native rate.
- Interpolate visual positions between simulation ticks to avoid stutter on high-refresh displays.

### Multitasking schedule

The original schedules different AI tasks at different frequencies — some run every frame, some every 2 frames, some every 4, 8, 16, 32, 64, 128, 256 frames (`SAM/EXEC.ASM`). This was a CPU-budget optimization for the 6809.

A remake can **run all AI every frame**; modern hardware has the budget. However, preserve the *philosophy* that some decisions (e.g., warrior squadron mission selection, planetoid swarm-trigger checks) are made on multi-second cadences rather than per-frame — this gives the AI its characteristic "thinking, then committing" feel rather than twitchy reactivity.

### Tick units in this spec

Throughout the spec:

- "Frame" means one 60Hz simulation tick = ~16.67ms.
- "Second" means 60 frames.
- Speed table units (`speed-tables.yaml`) are the original "nano-pixels per 16ms tick" — see the unit notes in that file. Treat speeds as relative tunables; the *shape* of each table matters more than absolute numbers.

## Entity workspace

The original ROM holds a fixed pool of up to **48 simultaneous live objects** (`tunables.yaml#max_objects`). When the pool is exhausted, no new entity can spawn until one despawns.

A remake **should not enforce a 48-entity cap**. The cap is a 6809 RAM constraint, not a design decision. However, the spawning *rate* (governed by population growth in `populations.yaml`) is a design decision — preserve it. If the remake removes the cap, ensure population growth still feels gradual rather than overwhelming.

## Camera and bounds

The viewport scrolls to follow the player with damping (`tunables.yaml#scroll_damping_time = 64 frames`). The viewport never instantly re-centers; it eases. This damping contributes to the floaty, momentum-driven feel.

`tunables.yaml#scroll_top/bottom/left/right` define the viewport's interior margins (the player's ship is kept within these screen boundaries by camera follow). These specific pixel values are tied to the original 256×224 display; a remake should re-derive equivalents for its own resolution while preserving the principle that the player is **near-centered with damping**, not instantly-centered.

## Implementation-free properties

A remake's world model must satisfy:

- 2D continuous space, no explicit map boundary
- Sub-tick precision for slow entities
- 60Hz fixed-step simulation
- A scanner that displays entity positions compressed from world space
- A camera that damps to follow the player
- Off-screen entities continue simulating (with possibly reduced fidelity)

A remake's world model does **not** need to:

- Match the original 256×224 viewport
- Match the original scanner cell scale
- Use the original 48-object cap
- Use the original multi-rate task scheduler
- Use the original L/S axis naming
