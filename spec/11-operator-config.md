# 11 — Operator Configuration

The arcade original exposes a service menu (accessed via the cabinet's
Advance button) with adjustable settings stored in CMOS-backed RAM. The
shipped settings, defaults, and persistence rules are catalogued in
`data/operator-defaults.yaml`.

A modern remake should expose the equivalent of these settings via a
**Settings** menu, persisted via platform-appropriate storage (filesystem,
profile, or cloud sync).

## Required settings

### Difficulty

`operator-defaults.yaml#difficulty_of_play`. Integer 1–5, **factory default
5** (verified `SAM/TB13.ASM:74`).

A modern remake should expose this with friendly labels. Note the original
ships at maximum:

| value | label                          |
|-------|--------------------------------|
| 1     | Easy                           |
| 2     | Normal                         |
| 3     | Hard                           |
| 4     | Brutal                         |
| 5     | Nightmare (factory default)    |

This setting affects DTime ramp speed and warrior aggression. See
`06-progression.md`.

### Extra ship thresholds

- `operator-defaults.yaml#first_extra_ship_at` — default **30,000 points**.
- `operator-defaults.yaml#additional_extra_ship_factor` — default **30,000 points**.

These are **separately configurable** in the original. A remake should
preserve both knobs (some players want frequent extras; some want one big
"reward" early then nothing).

Recommended UI: presets ("Generous: 5k / 5k", "Standard: 30k / 30k",
"Stingy: 50k / 100k") plus custom values.

### High score table reset

`operator-defaults.yaml#high_score_table_reset`. An action, not a value.
Resets both Immortals and Survivors Today to their seed defaults.

A remake should expose this as a button labeled "Reset High Scores" with
a confirmation dialog.

### Coinage

`operator-defaults.yaml#coinage`. Largely obsolete on non-cabinet
platforms. A remake can:

- **Hide entirely** if no cabinet/free-play mode is supported.
- **Expose under a "Cabinet Mode" toggle** for hobbyists running on
  arcade-style hardware.
- **Repurpose as a "Continue" pricing knob** if the remake supports
  microtransactions (recommended: don't).

### Marquee display

`operator-defaults.yaml#marquee_display`. Toggle for the title-screen
marquee in the attract loop. Default on.

### Operator message

`operator-defaults.yaml#operator_message`. Two-line custom text shown
during the marquee. Used by arcade operators to write messages like
"PLAY OUR PINBALL TOO" or naming the venue.

A modern remake might expose this as a "Personal motto" field (cosmetic,
shown in the player's profile or attract screen) — or omit entirely. Low
priority.

## Recommended modern additions

These do not exist in the 1983 original but are appropriate for a modern
remake:

- **Audio bus levels:** Master / Music / SFX / Voice / Ambience. Voice
  ducking enabled by default.
- **Voice subtitles:** Sinistar's lines as captions. Important for
  accessibility — the deliberate voice distortion can hurt intelligibility.
- **Colorblind palette options.**
- **Input remapping** (gamepad / keyboard / mouse).
- **Aim sensitivity / dead zone** (for analog stick aim).
- **Pause behavior:** suspend audio, dim screen, show overlay.
- **Reduce-motion mode:** dampen camera shake and explosion intensity.
- **Speech volume separate from SFX volume.**
- **Replay save/load** (if the remake supports replays).

## Out of scope

Do not implement:

- ROM/RAM/blitter/watchdog diagnostic tests.
- Color bar test, switch test, sound test (modern equivalents are
  Settings → Audio Test which is fine; the original's hardware-specific
  diagnostics are not).
- CMOS battery freshness alarm.
- Specific Williams cabinet quirks (coin slot mappings, ticket
  dispensers, etc.).

## Persistence

The original CMOS persists across power cycles. A remake should map
`persistence: cmos` to durable storage and `persistence: ram_session_only`
to in-memory state cleared on app launch.

Implementation suggestions:

- Local file (JSON, SQLite) for settings + Immortals table.
- Optional cloud sync for Immortals (online leaderboard).
- In-memory only for Survivors Today.

Privacy: all settings should be locally stored by default. Cloud sync
should be opt-in.
