# 09 — Audio

Sinistar's audio is the game's most distinctive feature. There are two
audio systems:

1. **Sound effects (SFX)** — game-event audio, see `data/sfx.yaml`.
2. **Speech** — Sinistar's voice, see `data/speech.yaml`.

These are catalogued by *what they convey to the player*, not by 1983
sound-board codes. The original waveforms (1980s synthesis on a 6800
sound CPU and CVSD-encoded speech) are reference, not requirement. A
modern remake should pick its own audio palette.

## SFX taxonomy

Sound effects are grouped by player-facing role:

### Player feedback

| event                  | role                                            |
|------------------------|-------------------------------------------------|
| `player_fire`          | Confirms primary shot fired.                    |
| `sinibomb_launch`      | Confirms sinibomb deployed (with bomb cost).    |
| `thrust`               | Continuous feedback of ship throttle.           |
| `bounce_collision`     | Object-on-object bump (player or otherwise).    |
| `player_pickup_crystal`| Crystal collected (+1 sinibomb to bay).         |
| `extra_ship_awarded`   | Score crossed extra-ship threshold.             |

### Threat indicators

| event                  | role                                            |
|------------------------|-------------------------------------------------|
| `warrior_alert`        | Squadron entering attack range.                 |
| `warrior_fire`         | Warrior fired at player.                        |
| `worker_grab_crystal`  | Worker grabbed a crystal — clock advancing.     |
| `worker_deliver_crystal` | Worker fed Sinistar — assembly progressed.    |
| `crystal_flash`        | Free crystal pulsing — pickup opportunity.      |

### Significant events

| event                  | role                                            |
|------------------------|-------------------------------------------------|
| `sinibomb_detonate`    | Sinibomb exploded (impact or auto-detonation).  |
| `player_death`         | Player ship destroyed.                          |
| `turn_start`           | New round / sector beginning.                   |
| `game_over`            | End of game.                                    |
| `message_alert`        | HUD message displayed.                          |
| `coin_insert`          | Cabinet credits added.                          |

## Priority and queueing

The original uses a strict priority queue (1–63, higher interrupts lower).
A modern audio engine should not literally reimplement this — modern
multi-voice mixers can play many effects simultaneously. But the *intent*
behind the priorities should be preserved through ducking and voice-stealing
heuristics:

- **High priority (≥40):** `sinibomb_detonate`, `player_death`, `extra_ship_awarded`, `turn_start`, `game_over`, `coin_insert`. These should never be missed; if the mixer is saturated, evict a lower-priority sound.
- **Medium priority (20–39):** `warrior_fire`, `worker_grab_crystal`, `worker_deliver_crystal`, `player_pickup_crystal`, `sinibomb_launch`, `message_alert`. Important but not catastrophic to drop.
- **Low priority (<20):** `bounce_collision`, `crystal_flash`, `thrust`, `player_fire`. Decorative; first to be voice-stolen.

## Speech catalogue

Sinistar's voice lines, with full triggers, are in `data/speech.yaml`.
Summary:

| line               | when                                            |
|--------------------|-------------------------------------------------|
| `i_am_sinistar`    | Power-on / attract; assembly begins.            |
| `i_hunger`         | Workers feeding Sinistar (incomplete).          |
| `beware_i_live`    | Sinistar fully assembled — boss-active stinger. |
| `beware_coward`    | Player avoiding engagement.                     |
| `run_coward`       | Sinistar pursuing.                              |
| `run_run_run`      | Sinistar imminent — bite range.                 |
| `i_hunger_coward`  | Aggressive feeding — Sinistar pursuing while incomplete. |
| `roar`             | Sinistar passes near player; critical state.    |
| `silence`          | Mute — flushes the speech queue.                |

### Voice channel

Speech runs on a **single dedicated voice channel**. New speech can:

- **Interrupt** lower-priority lines (`run_run_run` overrides `i_hunger`).
- **Queue** behind same-priority lines (rare; usually flushed).
- **Be flushed** by `silence` (e.g., on player death).

A modern remake should have a single audio bus dedicated to Sinistar's
voice and **duck SFX** (-3 to -6 dB) when speech plays. Speech must be
intelligible over combat noise.

### Suppression rules

Speech is **suppressed**:

- While player is dying (`DeaTime != 0`). Sinistar does not gloat.
- While Sinistar is dying.
- During warp-out / sector transition.

These suppression rules are deliberate pacing choices. **Preserve them.**

### Escalation curve

Sinistar's lines escalate as the boss closes on the player:

```
calm        ─── i_am_sinistar (announcement)
              │
                 i_hunger (workers feeding it)
              │
                 beware_i_live (alive!)
              │
                 beware_coward (you're running)
              │
                 run_coward (it's chasing)
              │
                 run_run_run (bite range)
              │
critical    ─── ROAR (close pass)
```

This curve is the spine of the game's emotional arc within a sector.
Any voice acting / synthesis for the remake should match this escalation —
calmer earlier lines, more aggressive / unhinged later lines.

## Voice acting guidance

The 1983 original uses a CVSD-encoded recording with low fidelity and
distortion that gives Sinistar an alien, fearsome quality. A modern
remake should:

- Cast a deep, distinctive voice. Not generic-villain.
- Apply processing to make Sinistar sound **non-human** — distortion,
  bit-crushing, harmonic shifts, formant manipulation. The lines should
  feel like they're coming from inside something massive, not from a
  person.
- Vary delivery across the escalation curve. Earlier lines flatter,
  later lines more guttural.
- Keep diction *crisp enough to understand* despite the distortion.
- Do not over-act. Sinistar is more menacing when restrained than when
  shouted — until `roar`, which should be unrestrained.

## Music

The original game is **silent during play** — no background music. Audio
texture comes entirely from SFX, ambient (`crystal_flash`, `thrust`),
and Sinistar's voice. This is unusual and effective; the lack of music
makes the speech and threat sounds more impactful.

A modern remake should consider:

- **Option A (canonical):** no music during play. Title / attract may
  have a theme. Game-over may have a sting. Sectors are silent except
  for SFX and voice.
- **Option B (modernized):** very low, ambient drone underscore that
  rises with threat level. Must not crowd the speech channel.

Option A is recommended for fidelity. If using Option B, ensure music
ducks aggressively when Sinistar speaks.

## Modernization notes

- Use sample-based audio for SFX, not synthesized. Modern players expect
  full-fidelity audio.
- Use voice acting for speech, not TTS or vintage synthesis. Voice is
  too important to compromise.
- Preserve all listed events as audio cues. The game's readability
  depends on consistent audio feedback.
- The "no music during play" choice is bold and iconic. Don't reflexively
  add music.
