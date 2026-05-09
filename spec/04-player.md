# 04 — Player

## Input

The original cabinet uses a **Williams 49-way joystick** — a directional
input device with 49 discrete positions giving near-analog feel. Plus two
buttons: **Fire** (primary shot) and **Sinibomb** (release homing weapon).

A modern remake should map input as follows, in priority order:

1. **Twin-stick gamepad**: left stick = movement, right stick or face button = fire, shoulder = sinibomb.
2. **Single-stick gamepad**: stick = movement (heading also = aim), one trigger = fire, other = sinibomb.
3. **Mouse + keyboard**: WASD = thrust direction, mouse direction = aim, click = fire, right-click or space = sinibomb.
4. **Touch / mobile**: virtual analog stick + on-screen fire/bomb buttons.

The 49-way fidelity matters because Sinistar's drift dynamics are sensitive
to direction precision. Modern analog inputs should give the player at least
as fine-grained directional control as the 1983 stick — i.e., **do not
quantize input to 8 directions**.

## Movement

The ship has **inertia**. Holding a direction does not produce constant
velocity; it produces constant *acceleration* along that direction. The ship
drifts when input is released. There is no instant-stop.

Implementation guidelines:

- Acceleration magnitude per frame is a tuning constant. The original uses a
  small per-frame velocity delta along the input vector; the value should be
  tuned to feel "responsive but floaty" — the player should be able to dodge
  but never feel locked-on-rails.
- Velocity has a soft cap. The original caps at a moderate speed (around what
  warriors fly at, so the player can keep pace with squadrons but not
  outrun Sinistar at full chase). Tune to match.
- Rotation (the ship's facing direction) follows input direction with no
  delay, OR follows velocity direction — implementation choice. The original
  keys facing to the joystick.
- Drag/friction is **light**. The ship coasts. This coasting is the core
  feel — heavier drag breaks the game.

## Firing

**Primary shot** (`event_id: player_fire`):

- Fires in the direction the ship is facing (or the joystick direction
  at fire-time — small distinction for the rare case where these differ).
- Inherits a fraction of player velocity plus a forward boost. The original
  uses 3× and 4× acceleration along heading axes. This means moving forward
  while firing = faster shots; moving backward = slower shots.
- Multiple shots may be on-screen. The original limits by free entity slots;
  a remake should allow at least 4 simultaneous player shots.
- Cooldown: brief (the original is essentially every frame the button is
  held, but with a short visual/audio cooldown). Tune to match.

**Sinibomb** (`event_id: sinibomb_launch`):

- Fires only if the player has at least 1 sinibomb in the bay
  (`tunables.yaml#max_in_bay = 20`).
- The sinibomb is a homing weapon. It seeks Sinistar, not the nearest enemy.
- See `02-entities.md#Sinibomb` and `speed-tables.yaml#stbl_sinibomb` for behavior.
- Decrements the bay count by 1 on launch.

## Lives

The player starts each game with a configured number of ships. The factory
default is **3** (`SAM/TB13.ASM:DEFALT` "SHIPS PER GAME" = `$03`). See
`operator-defaults.yaml#ships_per_game`.

**Earning extra ships:** see `07-scoring.md` and `operator-defaults.yaml#first_extra_ship_at`. Default: first extra at 30,000 points; subsequent every 30,000 points (operator-adjustable).

**Losing a ship (verified against `WITT/COLLISIO.ASM`):**

- Hit by a warrior shot (`PLAYER × WASHOT`, line 253-259) — instant death.
- Bitten by Sinistar in `alive` state (`SINIBITE` at line 85-126).
- Player–worker / warrior / planetoid collisions are **bounces, not deaths**
  (lines 56-70). The bounce dynamics make these dangerous (the player can
  be knocked into walls, into Sinistar, or out of position), but the
  collisions themselves don't kill the ship. The player ship dies primarily
  from warrior shots and Sinistar bites.

On death:

1. Player enters `dying` state. No input. Explosion sequence plays.
2. `event_id: player_death` SFX fires (priority 56, 128 ticks).
3. Speech is **silenced** (`speech.yaml#silence`) — Sinistar does not gloat.
4. After the death animation, if ships > 0, the player respawns at a safe
   position (typically near the screen center, away from immediate threats).
5. If ships == 0, transition to game-over (see `08-game-flow.md`).

The original allows the player to be respawned with **invulnerability frames**
to prevent immediate re-death from lingering threats. A remake should do the
same; ~2 seconds of invulnerability is reasonable.

## Sinibomb bay

The bay holds up to `tunables.yaml#max_in_bay = 20` sinibombs. Each crystal
collected by the player **via direct ship contact** adds 1 sinibomb to the
bay and awards 200 score. Player shots do **not** collect crystals; they
pass through (verified `WITT/COLLISIO.ASM:226`).

When the bay is already full, the next crystal collected is still consumed
but **no bomb is added**. The game plays a different tune
(`sfx.yaml#crystal_saved_for_warp`) and displays the message
**"CRYSTAL SAVED FOR WARP ENGINES"** (`WITT/COLLISIO.ASM:160-188`,
`AddBomb` at MAXBOMBS branch). This is a charming reassurance that the
"wasted" crystal isn't really wasted — it's saved for the warp drive after
the player kills Sinistar. (Mechanically, score increment behavior at the
overflow case should be preserved as in the original: crystal consumed,
no bomb, no extra points.)

The bay count is shown on the HUD.

## Ship warp (post-Sinistar kill)

When the player destroys Sinistar:

1. Sinistar enters `dying` state and shatters.
2. Player ship enters `warping` state.
3. Collisions are disabled.
4. Ship accelerates off-screen at `tunables.yaml#warp_velocity = 256`
   (in 6809 units; tune for remake).
5. The next sector spawns; the player ship is placed near the new sector's center.
6. Wave/difficulty advances one step.

## HUD

The status panel during play shows:

- Score (current player)
- Ships remaining
- Sinibomb bay count
- Sinistar's current piece-progress (how close it is to assembling)
- Scanner

Layout is implementation-free; the original uses `SAM/PANEL.ASM`. Modern
HUDs can re-style freely as long as all five elements are legible.

## Modernization notes

- The 49-way joystick is a hardware artifact; the *fidelity of directional
  input* is what matters. Don't quantize.
- Inertia and drift are non-negotiable. Any "snappy" control mod would
  fundamentally change the game.
- The bay cap of 20 is canon. Removing it (infinite bombs) breaks the
  crystal economy.
- Invulnerability-on-respawn is good practice (and was added as a mod —
  ShieldMod — in the SynaMax era). Treat as canonical for the remake.
