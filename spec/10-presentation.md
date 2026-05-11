# 10 — Presentation

This chapter draws the line between **what the remake must preserve** and
**what the remake can reinterpret** in audio-visual presentation.

The principle: **mechanics and feel are canon; pixels and waveforms are not.**

## Must preserve

These are the player-facing properties that define Sinistar. A remake that
drops any of these is no longer Sinistar.

### 1. Sinistar's voice

Every line in `data/speech.yaml`. The escalation curve from announcement →
hunger → alive → cowardice taunts → roar. The single-channel rule. The
suppression-during-player-death rule. See `09-audio.md`.

### 2. The scanner

A panel showing entity positions across the entire sector, compressed into
a small radar view. The scanner is the player's primary peripheral
threat awareness. See `01-world-model.md`.

### 3. Momentum control

The ship has inertia and drift. Direction input is fine-grained (not
8-way). See `04-player.md`.

### 4. The crystal economy

Workers carry crystals to Sinistar. Player intercepts crystals to gain
sinibombs and starve the boss. Sinistar can only be killed by sinibombs.
See `02-entities.md` and `05-ai.md`.

### 5. The chase curve shape

Sinistar's pursuit speed is non-monotonic — surge, pause, surge — giving
the iconic "winding up" feel. See `speed-tables.yaml#stbl_sinistar_chase`.

### 6. Visual readability of state

- **Sinistar's assembly progress** must be visible in-world (not just on
  HUD). The original shows pieces fitting in.
- **Workers carrying crystals** must be visually distinct from idle workers.
- **Free-floating crystals** must pulse/glow to attract attention.
- **Warriors** must visibly aim before firing (turret rotation in original).

### 7. Sound-to-event correspondence

Every event in `data/sfx.yaml` must have an audio cue. The audio language
of the game (what each sound means) is part of the design.

### 8. The two-table high-score system

SINISTAR Immortals (persistent) and SURVIVORS TODAY (session). See
`08-game-flow.md` and `07-scoring.md`.

### 9. Silent gameplay (no background music)

See `09-audio.md`. A remake may add ducked ambient, but the *option to
play in silence* with only SFX and voice should be available — and is
recommended as default.

## Reinterpretable

These are reference, not requirement. A remake can reimagine them.

### Visual style

The original is 1983 raster CRT with a 16-color palette at 256×224
resolution. A remake can use:

- Modern HD or 4K resolution
- Any color depth
- Any art style (2D pixel, 2D vector, 3D, abstract, photorealistic)
- Any aspect ratio (the original is roughly 4:3)
- Any rendering technique (sprites, particles, post-processing, shaders)

### Sprite art

The Sinistar's specific skull-and-jaw silhouette is iconic but not
sacred. As long as the entity reads as **enormous, mouth-forward, and
fearsome**, the art is open. Same for ship, workers, warriors, planetoids —
the silhouettes should be *role-readable*, but the specific art is open.

The 1983 sprite dimensions in `data/entities.yaml` (`approx_pixel_size`)
are reference proportions, not a target.

### Audio synthesis

The original's 6800-synthesized SFX and CVSD-compressed speech are part
of arcade history but not part of Sinistar's design DNA. A remake should
record fresh voice acting and use modern audio production. See `09-audio.md`.

### Particle effects

The original's explosions are sprite-based with fragments tumbling
outward. A modern remake should use particle systems with smoke, sparks,
glow. The *catastrophic feel* of a Sinistar shatter should be preserved;
the technique is open.

### HUD design

The original HUD layout is a single bar at the bottom with score, ships,
sinibomb count, and scanner. A remake can redesign:

- Modern HUD aesthetics (transparent overlays, screen-edge clusters, etc.)
- Diegetic HUD (info shown on/near the ship)
- Dynamic HUD (elements appear when relevant)

The five required elements (score, ships, sinibombs, Sinistar progress,
scanner) must all be visible.

### Aspect ratio and viewport size

Original: 256×224, roughly 4:3. A remake can:

- Use modern 16:9 / 21:9 / 16:10
- Show more of the sector at once (changes feel — more breathing room)
- Show less and use scrolling more aggressively (changes feel —
  more claustrophobic)

The choice affects gameplay character. **Recommended:** match the original's
density of on-screen action. Showing too much makes the game feel less
threatening.

### Cabinet vs platform

The original is an upright arcade cabinet with a 49-way joystick and two
buttons. A remake can target:

- PC (mouse + keyboard, gamepad)
- Console (gamepad)
- Mobile (touch)
- VR (treat carefully — momentum + voice in 3D might be intensely
  effective, but the scanner concept needs reimagining)
- Modern arcade cabinet (preserve original input, but with HD screen)

## Out of scope (don't bother)

These exist in the original due to hardware constraints, not design intent.
A remake should ignore them entirely.

- Watchdog timer "stroking" (the 8-VBLANK reset prevention)
- Memory banking, ROM/RAM partitioning
- 6809 / 6800 CPU partitioning between game logic and sound
- Williams blitter chip
- 49-way joystick reading (any analog input is fine)
- CMOS battery-backed RAM specifically (any persistent storage works)
- TMS5220-style speech synthesis specifically (any audio works)
- ROM/RAM diagnostic tests, color bar test, switch test
- 60Hz raster lock specifically — modern displays handle frame timing
  differently. The simulation rate (`tunables.yaml#tick_rate_hz`) is
  the canonical 60Hz value; raster lock is hardware artifact.
- The DMA-driven sprite scheduler

## Modernization recommendations

If the remake team is looking for ways to elevate the original beyond
fidelity:

- **Procedural sector backdrops** that read as different "regions of
  space" (gas clouds, asteroid fields, deep void) for each wave. The
  original uses a star field; modern volumetrics could be stunning.
- **Dynamic music ducking against speech** if music is added.
- **Accessibility:** colorblind-friendly entity palettes, screen-reader
  HUD, configurable text size, captions for speech (especially given
  the deliberately distorted voice).
- **Save / continue between sectors** for non-arcade contexts. The
  original's "one credit, one game" is arcade tradition; modern players
  expect persistent progress.
- **Replays and ghosts** for high scores. Watching the world record is
  part of the genre's culture.
- **VR / spatial audio** would be a natural fit for the scanner-driven
  threat awareness mechanic.
