# 06 — Progression and Difficulty

## Wave structure

Sinistar uses a fixed wave sequence with a tutorial wave (0) and four
repeating combat waves (1–4). After wave 4, the sequence loops back to
wave 1 — but **DTime (the master difficulty counter) does not reset**. So
each loop is harder than the last.

Wave populations are in `populations.yaml`:

| wave   | name              | character                                            |
|--------|-------------------|------------------------------------------------------|
| 0      | Void Zone         | Tutorial. No warriors. Lots of small planetoids.     |
| 1      | First Combat      | Workers + warriors arrive. Few planetoids.           |
| 2      | Worker Zone       | Many workers — Sinistar assembles fast.              |
| 3      | Warrior Zone      | Warriors dominate — combat-heavy sector.             |
| 4      | Planetoid Zone    | Asteroid-dense — navigation challenge.               |
| (loop) |                    | Wave 1 repeats with higher DTime — escalation.       |

## Sector advance

A sector ends when the player **destroys Sinistar**. A fully-assembled
Sinistar requires `tunables.yaml#pieces_required = 12` sinibomb hits; each
hit removes one body piece, and destruction triggers when the body-piece
counter reaches zero. After the destruction:

1. Sinistar shatters (`02-entities.md#Sinistar` dying state).
2. Player warps off-screen (`04-player.md#Ship warp`).
3. The next wave loads. Player ship spawns near sector center.
4. Wave index advances (wraps at wave 4 → wave 1, never returns to wave 0).
5. DTime continues climbing.

The player's bay is **preserved** across sectors — sinibombs the player has
saved up carry forward. The score is preserved (it never resets in a single
game).

## DTime — the difficulty counter

DTime is a 16-bit counter that increments by `populations.yaml#difficulty.dtime_increment_per_frame = 6` each frame. It governs how fast enemy populations grow within a wave.

### Population growth

Each wave defines target populations (see the `populations` field per wave).
At wave start, the live population is set per the table. As DTime climbs,
the *desired* population for each entity type increases linearly:

```
desired[type] += slope[type] * (DTime - last_DTime) / 256
if floor(desired[type]) > current[type] and entity_pool_has_room():
    spawn_one(type)
```

Slopes (`populations.yaml#difficulty.{worker,warrior}_growth_slope`):

- Workers: `+16` per DTime unit
- Warriors: `-8` per DTime unit (yes, negative — warriors thin out within a single wave; they spawn primarily at wave-start)

Planetoid slopes are per-type and similarly tuned.

### Operator difficulty knob

The operator's `difficulty_of_play` setting (1–5, **factory default 5**,
verified `SAM/TB13.ASM:74`) modulates how aggressively DTime climbs and
how high `_WAgg` (warrior aggression) peaks:

- First sector (wave 0): DTime is pre-advanced by `difficulty * operator_difficulty_multiplier_first_zone = difficulty * 10`.
- Subsequent sectors: DTime is pre-advanced by `difficulty * operator_difficulty_advancement_subsequent_zones = difficulty * 6`.

Higher difficulty → faster ramp → enemies escalate more quickly within each sector.

### Warrior aggression (`_WAgg`)

Warrior aggression scales the rate at which warriors choose `INTERCEPT` over
`DRIFT` and the closeness of their attack passes. `_WAgg` is incremented
by `127` per wave transition (`populations.yaml#difficulty.warrior_aggression_delta_per_wave`),
producing more aggressive warriors in later sectors.

## Pacing within a sector

Within a single sector, the typical arc is:

1. **0–10 seconds:** wave populations spawn. Sinistar assembling.
   Workers begin mining. First crystal exchanges happen. Player explores,
   collects early crystals.
2. **10–30 seconds:** warriors begin first attack runs. Sinistar speech
   shifts from `i_am_sinistar` to `i_hunger`. First swarm trigger may fire.
3. **30–60 seconds:** Sinistar nears full assembly. Speech escalates to
   `beware_i_live`. Warriors more aggressive. Player must have stockpiled
   sinibombs.
4. **60+ seconds:** Sinistar alive and chasing. Player has limited window
   to land enough sinibombs to strip all remaining body pieces while evading
   bite, warriors, and worker attrition.

Time-to-Sinistar varies with wave (worker count) and difficulty. The above
is a rough envelope, not a strict timer — the game's clock is the
crystal economy, not real time.

## End conditions

A game ends when the player runs out of ships (game-over). There is no
"game complete" state — waves loop forever. Top-tier players are expected
to reach high scores measured in millions.

## Modernization notes

- The DTime counter is an excellent design pattern; preserve it as-is.
  Modern games often hand-tune per-wave parameters; Sinistar's continuous-
  growth model is more elegant and gives smoother difficulty.
- The wave-1-loops-with-rising-DTime structure means waves 1–4 are never
  truly repeated — they always feel harder. Preserve this.
- The negative warrior slope within a wave is subtle but important: it
  means warriors arrive in pulses (front-loaded at wave-start) rather than
  steadily accumulating. This gives moments of relative calm.
- Operator difficulty (1–5) should be exposed in the remake's settings,
  ideally with names ("Easy / Normal / Hard / Brutal / Nightmare") rather
  than just numbers.
