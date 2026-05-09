# 07 — Scoring

## Score values

The complete event-to-points mapping is in `data/scoring.yaml`. Summary:

| event                       | points  |
|-----------------------------|---------|
| Destroy Sinistar (full)     | 15,000  |
| Destroy Sinistar piece      | 500     |
| Kill warrior                | 500     |
| Kill worker                 | 150     |
| Kill warrior shot           | 100     |
| Collect crystal (player)    | 200     |
| Destroy planetoid           | 5       |

A few design notes about these values:

- **Sinistar destruction (15,000)** is the dominant single-event score.
  Sectors are won, not survived; a skilled player accumulates score
  primarily by clearing sectors.
- **Warriors > workers** because warriors threaten you actively; workers
  threaten you indirectly (via Sinistar assembly).
- **Crystals (200) are deliberately worth less than warrior kills** — the
  primary reward of crystals is the *sinibomb*, not the points.
- **Planetoids (5)** are nearly worthless score-wise. They are obstacles
  and crystal sources, not score targets. Don't reward smashing them.
- **No combo / multiplier system.** Sinistar's score is flat. Modern
  remakes that add multipliers should make them optional / cosmetic; flat
  scoring rewards the right strategic priorities.

## Score storage and display

The original stores score as 8-digit BCD (4 bytes) per player. Maximum
displayable: 99,999,999. A modern remake can store as int64 internally
but should preserve the 8-digit display cap (rolling over visually rather
than expanding to more digits).

## Extra ships

The player earns extra ships at score thresholds configured by the operator
(see `operator-defaults.yaml#first_extra_ship_at` and
`#additional_extra_ship_factor`).

**Defaults:**

- First extra ship at: **30,000 points**
- Each subsequent extra ship: every **30,000 points** thereafter
  (so 60,000, 90,000, 120,000, …)

**Award logic:**

- Track a `next_extra_ship_threshold` (initialized to `first_extra_ship_at`).
- After each scoring event, if `score >= next_extra_ship_threshold`:
  - Award one ship.
  - Play `event_id: extra_ship_awarded` (`sfx.yaml`).
  - `next_extra_ship_threshold += additional_extra_ship_factor`.
- Clamp ships at a sensible maximum (the original RAM has limits; a remake
  should pick a reasonable cap, e.g., 9 ships).

**Historical note:** the original development default for the first extra
ship was 5,000 points; raised to 30,000 for the shipped ROM to make extra
ships harder to earn. The "ExtraShipFix" mod restores 5,000. In the remake,
allow operators to choose; document 30,000 as the canonical default.

## Two-player alternating play

The original supports two-player alternating play:

- Each player has their own score, ships, sinibomb bay, and Sinistar
  progress within the current sector.
- On player death, if the other player still has ships, switch to that
  player's turn.
- High score entry is per-player at game-end.

A modern remake can drop alternating play (most modern players play solo)
or reimagine it as local co-op. The *spec* preserves alternating play as
documented behavior; whether to ship it is a remake-team decision.

## High-score tables

There are **two** high-score tables (see `operator-defaults.yaml#high_score_defaults`):

- **SINISTAR Immortals (CMOS / persistent):** 5 entries. Survives power
  cycle. Default seed = 30,000 with developer credits as initials.
- **Survivors Today (RAM / session):** 5 entries. Resets each power-on.
  Default seed = 10,000 with default initials.

Both tables show in the attract loop. The Immortals table cultivates
long-term aspiration; the Survivors Today table encourages immediate
return play during a single arcade session.

A modern remake should preserve both tables conceptually:

- *Immortals* → persistent leaderboard (local file, cloud, or hybrid).
- *Survivors Today* → reset on app launch / session start.

## Initials entry

When the player's final score qualifies for either table:

1. Game-over sequence completes.
2. Initials-entry UI launches. Player enters 3 characters via joystick:
   left/right cycles characters (A–Z, digits, dash, space), button
   confirms one position, then advances. After 3 characters, the entry
   is committed.
3. The new entry is sorted into the appropriate table(s).

The original character set is documented in `operator-defaults.yaml#initials_configuration`. A remake can offer a wider character set or
keyboard-style entry on appropriate platforms.

## Modernization notes

- Score values are canon. Don't rebalance.
- Display format (8 digits, leading zeros optional) is canon. A 10-digit
  display would feel wrong.
- Extra-ship thresholds are operator-configurable; default is 30k / 30k.
- Two-table high-score system is a strong design and should be preserved;
  the *names* ("Immortals" vs "Survivors Today") are evocative and worth
  keeping.
- Online leaderboards are an obvious modernization addition — but make them
  *additive*, not a replacement for the local Immortals table.
