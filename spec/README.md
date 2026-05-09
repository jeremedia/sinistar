# Sinistar 2026 — Implementation-Independent Specification

This directory contains a complete specification for **Sinistar 2026**, a
modern remake of the 1983 Williams arcade game *Sinistar*. The spec is
derived from the rebuilt 1983 ROM source code in this repository.

The spec is **implementation-independent**: it does not prescribe an engine,
language, art style, or audio pipeline. It captures the game's mechanics,
AI, audio cues, voice content, and progression — the things that make
Sinistar *Sinistar* — and explicitly liberates the remake team from
1983 hardware constraints.

## Design pillars

A faithful Sinistar 2026 must preserve five things:

1. **Voice as the primary fear vector.** Sinistar speaks. Its lines
   escalate. Voice is more important than visuals.
2. **Claustrophobic awareness via the scanner.** The player sees a slice
   of the sector and a compressed scanner. The threat is heard before it
   is seen.
3. **Momentum-based control.** The ship has inertia and drift. No
   snap-stops.
4. **Escalating dread, not escalating numbers.** Sinistar's chase curve
   surges, pauses, then surges again — the iconic "winding up" feel.
5. **The crystal economy is the clock.** No level timer; the time pressure
   is workers feeding Sinistar.

Full discussion in [`00-overview.md`](00-overview.md).

## Reading order

| chapter | topic                                          |
|---------|------------------------------------------------|
| [00](00-overview.md) | Pitch, design pillars, scope               |
| [01](01-world-model.md) | World, time, coordinates, scanner       |
| [02](02-entities.md) | Entity catalog and state machines           |
| [03](03-physics-collision.md) | Velocity, bounce, collision matrix |
| [04](04-player.md) | Input, firing, lives, warp                    |
| [05](05-ai.md) | Worker / Warrior / Sinistar / Planetoid AI        |
| [06](06-progression.md) | Wave model, DTime, difficulty           |
| [07](07-scoring.md) | Points, extra ships, high scores             |
| [08](08-game-flow.md) | Attract loop, status, game-over            |
| [09](09-audio.md) | SFX taxonomy and Sinistar voice catalog        |
| [10](10-presentation.md) | Must-preserve vs reinterpretable         |
| [11](11-operator-config.md) | Settings and persistence              |
| [12](12-glossary.md) | Terms                                       |

**For a 30-minute read** to understand the design: 00, 02, 05, 10.

**For implementation:** all chapters, plus `data/`.

## Machine-readable data

`data/` contains YAML files that are the **authoritative source for
numeric values**. Prose chapters reference these by id.

| file                         | content                                  |
|------------------------------|------------------------------------------|
| [`data/entities.yaml`](data/entities.yaml) | Entity catalog: stats, scoring, descriptions |
| [`data/scoring.yaml`](data/scoring.yaml) | Score values per event              |
| [`data/tunables.yaml`](data/tunables.yaml) | Gameplay constants (orbits, vibration, etc.) |
| [`data/populations.yaml`](data/populations.yaml) | Per-wave entity counts + difficulty growth |
| [`data/speed-tables.yaml`](data/speed-tables.yaml) | AI distance→speed/accel tables |
| [`data/sfx.yaml`](data/sfx.yaml) | Sound effects keyed by gameplay event |
| [`data/speech.yaml`](data/speech.yaml) | Sinistar voice lines and triggers |
| [`data/operator-defaults.yaml`](data/operator-defaults.yaml) | Settings menu and CMOS defaults |

A remake can load these YAMLs directly as content data.

## Verification

`verification/` contains pseudocode samples that re-derive specific game
behaviors from this spec alone (without consulting the asm). They serve as
sanity checks that the spec is sufficient to implement the game.

See [`verification/README.md`](verification/README.md).

## What this spec is not

- **Not a port specification.** It does not describe how to translate 6809
  assembly into modern code.
- **Not an art bible.** It describes entity *roles* and *required
  readability*, not specific art direction.
- **Not an audio score.** It describes SFX *roles* and the speech
  *catalogue*, not specific waveforms or recordings.
- **Not exhaustive.** Where original behavior is unclear or
  hardware-coupled, the spec marks it as needs-research or as
  modernization-discretion.

## Provenance

Every YAML record cites its source file and symbol in the original asm
via a `source:` field. The spec was derived from:

- `SAM/` — Sam Dicker's engine, player, Sinistar entity, scheduler
- `WITT/` — Rich Witt's gameplay logic, AI, collisions, lipsync
- `FALS/` — Noah Falstein's populations, planetoids, speech triggers
- `MICA/` — RJ Mical's attract, status, high-score, explosions
- `VSNDRM9.ASM` — Mike Metz's sound ROM (SFX catalog)
- `SPEECH.ASM` — John Kotlarik's speech ROM (voice catalog)
- `README.md` — Project history and SynaMax's reverse-engineering notes

Mods (SAMTAIL, ShieldMod, MarqueeFix, ExtraShipFix, etc.) are explicitly
**not canon** for this spec, though they are noted in context where they
illuminate design decisions.

## License and attribution

The original Sinistar is © 1982/1983 Williams Electronics, Inc. This
spec is a derivative analytical work intended to enable a modern remake.
Credits to the original team:

- John Newcomer (concept, design)
- Sam Dicker, Noah Falstein, RJ Mical, Rich Witt (programmers)
- Jack Haeger (artist)
- Mike Metz (sound)
- John Kotlarik (speech)
- Ken Lantz (additional engineering)

And to SynaMax for the 2024 source rebuild that made this spec possible.
