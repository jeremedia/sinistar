# 08 — Game Flow

## Top-level state machine

```
                    ┌───────────────┐
                    │   Power-on    │
                    └───────┬───────┘
                            ▼
                    ┌───────────────┐
                    │  Boot / Init  │  load CMOS, init RAM, factory reset?
                    └───────┬───────┘
                            ▼
        ┌──────────────►Attract Loop◄───────────┐
        │           ┌───────┬───────┐           │
        │   ┌───────┘       │       └────────┐  │
        │   ▼               ▼                ▼  │
        │  HSTD       Marquee Title      Demo   │
        │ (~5s)         (~5s)         Gameplay  │
        │   │               │           (~30s)  │
        │   └───────┬───────┴───────┬───────┘   │
        │           ▼               │           │
        │      Coin / Start? ──no───┘           │
        │           │yes                         │
        │           ▼                            │
        │     ┌─────────────┐                    │
        │     │ Status Page │ (player turn intro)│
        │     └─────┬───────┘                    │
        │           ▼                            │
        │     ┌─────────────┐                    │
        │     │  Play Turn  │◄──────────┐        │
        │     └─────┬───────┘           │        │
        │           ▼                   │        │
        │     player died? ──ships>0──► respawn  │
        │           │ships=0                     │
        │           ▼                            │
        │     ┌─────────────┐                    │
        │     │  Game Over  │                    │
        │     └─────┬───────┘                    │
        │           ▼                            │
        │     score qualifies?                   │
        │           │yes      │no                │
        │           ▼         │                  │
        │     Initials Entry  │                  │
        │           │         │                  │
        │           ▼         ▼                  │
        └───────────┴─────────┘                  │
                                                 │
                    (loops back to attract)──────┘
```

## Attract loop

Three screens cycle continuously while no game is in progress:

### 1. High-score display (HSTD)

- Two tables visible simultaneously:
  - **SINISTAR Immortals** (persistent, 5 entries)
  - **SURVIVORS TODAY** (session, 5 entries)
- Top entry of each is highlighted as the "Highest" row.
- Title above: "SINISTAR — SINISTAR" (split horizontally).
- Duration: ~5 seconds.

### 2. Marquee title

- Large logo / title art.
- Trademark and copyright text.
- Custom operator message (two lines, configurable per
  `operator-defaults.yaml#operator_message`).
- "Insert Coin" / "Press Start" prompt.
- Duration: ~5 seconds.

### 3. Demo gameplay

- An automated "AI player" demonstrates gameplay:
  - **Phase 1 (~0.5–1s):** demo ship collects sinibombs (≥4 needed in
    the original; later builds patch to 8).
  - **Phase 2 (~10s):** demo bombs the Sinistar. Workers spawn at
    intervals (~every 8 seconds in the original demo).
  - **Phase 3 (~3–4s):** sleep, then exit.
- Duration: ~30 seconds total.

The cycle repeats: HSTD → Marquee → Demo → HSTD → … until a player starts
a game.

A modern remake on a non-cabinet platform may shorten or remove the demo
gameplay phase, but should retain HSTD and a title screen for parity with
the genre.

## Boot sequence

On power-on (or app launch):

1. Initialize RAM. Detect first-boot vs warm-boot via CMOS sentinel.
2. If first boot or factory reset triggered: seed CMOS defaults
   (high-score table, operator message, coinage, extra-ship thresholds).
   See `operator-defaults.yaml`.
3. Initialize attract-mode RAM (Survivors Today table).
4. Enter attract loop.

## Starting a game

When the player presses Start (with credits available, or in free-play
mode):

1. Attract loop exits.
2. **Status Page** displays:
   - Current player number (P1 / P2)
   - Player's score
   - Player's ships remaining
   - Sinibomb bay count
   - Sinistar's piece count (assembly progress, if returning to a sector
     with Sinistar partially built)
   - Or, if returning from Sinistar destruction:
     "CONGRATULATIONS — YOU DEFEATED THE SINISTAR"
3. Play turn-start jingle (`sfx.yaml#turn_start`).
4. Silence speech queue.
5. Initialize the sector (spawn entities per current wave's populations).
6. Player ship spawns near sector center.
7. Hand control to player — gameplay begins.

## Gameplay

Continuous play continues until:

- Player kills Sinistar (12 sinibomb hits against a fully-assembled
  Sinistar; fewer only if body pieces were removed before full assembly)
  → warp out → next sector loads → status page → next sector gameplay.
- Player ship is destroyed:
  - If ships remaining > 0: explosion sequence (~2 seconds),
    invulnerability respawn near safe location, gameplay resumes.
  - If ships remaining == 0: transition to game-over.

## Game over

1. Display "GAME OVER" message (~4–5 seconds).
2. Final score is fixed.
3. If two-player game and the other player still has ships, switch turns
   (back to step 1 of "Starting a game" for the other player). Otherwise:
4. Score qualification check:
   - If `score > min(Immortals)` or `score > min(Survivors Today)`:
     enter Initials Entry.
   - Else: sleep ~4 seconds, return to attract.

## Initials entry

1. UI displays the player's score and qualified table(s).
2. Three character positions, one at a time:
   - Joystick left/right cycles A–Z / digits / dash / space.
   - Joystick up/down may also be used.
   - Button confirms current character, advances to next position.
3. After 3 characters, sort entry into table.
4. Sleep ~1 second per player, then return to attract.

A modern remake on platforms with keyboards / virtual keyboards may offer
direct text entry. Preserve the 3-character cap (it is iconic and ensures
all entries fit the table layout).

## Pause

The original ships **without** a pause function (arcade tradition). The
PauseMod adds Player-1-button pause; this mod is not canon for the spec,
but a modern remake **should** include a pause. Recommended: pause shows
a discreet "PAUSED" overlay; resumes on button press; suspends all game
state (timers, AI, audio).

## Modernization notes

- The attract loop is essential for arcade authenticity but optional on
  modern platforms. Consider making the title screen the home view and
  optionally cycling demo footage as a screensaver.
- The two-table high-score system is worth preserving (see `07-scoring.md`).
- Pause is a modern necessity. The original's omission is a hardware/
  cabinet artifact, not a design choice.
- The "GAME OVER → Initials Entry → Attract" flow is canonical and worth
  keeping intact for the score-attack feel.
