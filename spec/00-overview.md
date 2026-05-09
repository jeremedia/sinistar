# 00 — Overview

## What this spec is

This is an **implementation-independent specification for Sinistar 2026**, a modern remake of the 1983 Williams arcade game *Sinistar*. The spec is derived from the rebuilt 1983 ROM source code in this repository (SynaMax's 2024 retargeting), but contains **no 6809 assembly, no hardware-specific implementation details, and no prescriptions about engine, language, art pipeline, or audio synthesis**.

The spec describes:

- What entities exist and how they behave
- How the AI thinks
- How physics, collisions, scoring, and progression work
- How the game flows from attract through game-over
- Which sounds and which spoken lines fire when
- What the operator can configure

It does **not** describe:

- Any specific palette, sprite art, or screen resolution
- Any specific audio synthesis or speech codec
- Any specific platform, engine, or programming language
- Any 6809 / 6800 / TMS5220 hardware assumptions
- Any code from the original ROMs

## Scope

**In scope:** the shipped 1983 ROM (the "factory" production version). Mods (MarqueeFix, SAMTAIL, ShieldMod, ExtraShipFix, etc.) are explicitly out of scope for canon, though `operator-defaults.yaml` notes a few of their adjustments as historical context.

**Out of scope:**

- The 1982 AMOA prototype build
- Diagnostic ROMs, ROM/RAM/switch test menus
- Mods and debug toggles
- Cabinet-specific hardware (coin slots, watchdog, blitter chip, raster timing)

## Design pillars

Sinistar 2026 should feel like Sinistar. Not look like it — *feel* like it. Five pillars define the feel:

### 1. Voice as the primary fear vector

Sinistar speaks. The spoken lines — *"BEWARE, I LIVE", "I HUNGER", "RUN, COWARD!"* — are the game's iconic identity. The Sinistar's voice escalates in aggression as it closes on the player. This voice work is more central to the game than any single visual element. **Preserve every line. Preserve the escalation curve. Preserve the rule that speech is suppressed during player death.**

### 2. Claustrophobic awareness via the scanner

The player cannot see the whole sector. They see what's on screen plus a compressed scanner showing nearby threats. The Sinistar can be heard, half-seen on the scanner, before it ever reaches the player's screen. This *peripheral dread* — knowing the threat is coming before you can see it — is the core tension. **The scanner is non-negotiable. Its visual style is open, its function is fixed.**

### 3. Momentum-based control

The player ship has inertia. It does not snap-stop. The Williams 49-way joystick gave near-analog directional input; the ship accelerates along the input vector and drifts. **Preserve the drift.** Snap-to-axis controls would break the game's tactility.

### 4. Escalating dread, not escalating numbers

Sinistar's chase speed table is **non-monotonic** — it surges at medium range, lulls slightly, then closes hard. This produces the signature feeling that the boss is "winding up" to strike. Combined with progressive worker activity, warrior aggression, and the Sinistar's own voice cues, the game escalates emotionally rather than numerically. **Preserve the chase curve shape, even if absolute values change.**

### 5. The crystal economy is the clock

There is no level timer. The clock is *workers delivering crystals to assemble Sinistar*. Every crystal a worker delivers shortens the time the player has. Every crystal the player intercepts both extends that time and arms the player's only Sinistar-killing weapon. This dual-purpose resource is the engine of the game's tension. **Preserve the dual purpose.**

## What "modernized presentation" means

Per scope decisions, the remake should:

- Use modern art and animation. The game does not need to look like a 1983 raster CRT.
- Use modern audio synthesis or sample-based audio. SFX waveforms are open.
- Use voice acting for Sinistar lines. The line *content* is canon; the *delivery* is reinterpretable, but should feel deliberately unsettling.
- Use platform-appropriate input (gamepad analog stick, mouse-aim, twin-stick, touch).
- Run at any modern resolution and refresh rate.

The remake should **not**:

- Reinterpret core mechanics. Sinistar is killed only by sinibombs; sinibombs come from crystals; warriors and workers behave as specified; the boss assembles from crystals delivered by workers; speech triggers fire on the documented conditions.
- Add features that change the loop (no upgrades, no shop, no procedural levels beyond wave cycling). Those are out of scope for fidelity.
- Skip the operator menu's spirit — even on a non-cabinet platform, expose difficulty and extra-ship thresholds.

## How to read this spec

Each numbered chapter (`01-…` through `12-…`) covers one subsystem. Each chapter cross-references the YAML data files in `data/` for tunable values; values quoted inline in prose link to a YAML row by id. The chapters are ordered so each builds on the previous:

1. World model → 2. Entities → 3. Physics → 4. Player → 5. AI → 6. Progression → 7. Scoring → 8. Game flow → 9. Audio → 10. Presentation → 11. Operator config → 12. Glossary

A reader who only wants to understand the design should read 00, 02, 05, 10. A reader implementing the game should read all of them and treat `data/` as authoritative for numeric values.
