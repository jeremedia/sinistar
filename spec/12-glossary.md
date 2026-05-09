# 12 — Glossary

Terms used throughout this spec.

**AMOA prototype** — The November 1982 Amusement & Music Operators Association
build of Sinistar (a pre-release shown to operators). Distinct from the
shipped 1983 ROM. **Out of spec scope.**

**Assembly** — The process of Sinistar being built from delivered crystals.
Sinistar is `absent` → `assembling` → `alive`. See `02-entities.md`.

**Attract loop** — The continuous demo cycle (HSTD → Marquee → Demo) that
plays when no game is in progress. See `08-game-flow.md`.

**Bay** — The player's sinibomb storage, capped at `tunables.yaml#max_in_bay = 20`. Each crystal collected adds 1.

**Bite** — Sinistar's attack. When the player ship enters Sinistar's mouth
hitbox, the player dies.

**CMOS** — In the original, battery-backed non-volatile RAM holding high
scores and operator settings. Generalized in the spec to "persistent
storage." See `11-operator-config.md`.

**CIRCLE=256** — The original's angular unit: 256 ticks = 360°. So 128 ticks
= 180°, 192 = 270°, etc. Used in formation angle constants.

**CVSD** — Continuously Variable Slope Delta Modulation. The original's
speech compression scheme. **Hardware artifact**, not in spec scope.

**Crystal** — Dual-purpose collectible. Workers carry to Sinistar (bad);
player intercepts for ammo and points (good). See `02-entities.md#Crystal`.

**Demo gameplay** — Phase of the attract loop where an AI plays the game
to demonstrate it. See `08-game-flow.md`.

**DTime** — The master difficulty counter that increments each frame.
Drives population growth within and across waves. See `06-progression.md`.

**Forming / formed** — Older terminology in the source for what this spec
calls `assembling` / `alive`.

**Fragment** — Inert visual debris from explosions. No collision, no AI.
See `02-entities.md#Fragment`.

**HSTD** — High-Score Table Display, the high-scores screen in the
attract loop.

**Immortals** — The persistent, CMOS-backed high-score table. 5 entries.
Seed value 30,000.

**InPop tables** — The original's per-wave initial population tables
(`InPop0`, `InPop1`, etc.). Captured in `populations.yaml`.

**Inhibitor** — The warrior shooting cooldown (`tunables.yaml#shooting_inhibitor_max`). Counts down only on-screen.

**L-axis / S-axis** — The original's "long" and "short" axes (horizontal
and vertical). 6809-era naming. Use **x / y** in modern remakes.

**Lipsync offset** — The encoded distance offset (`tunables.yaml#lipsync_offset = 412`) used during Sinistar's mouth animation to prevent self-collision. **Implementation artifact** — modern collision systems can simply exclude the mouth bone.

**Mouth offset** — The horizontal/vertical offset from Sinistar's sprite
origin to its mouth (`tunables.yaml#mouth_offset_long`,
`#mouth_offset_short`). The bite hitbox center.

**Operator** — The arcade machine owner / operator. The "operator menu"
is the service menu they use to configure the cabinet. See
`11-operator-config.md`.

**Orbit factor** — A unit-free scaling value used by AI to define orbital
distances. Lower = closer orbit. See warrior / worker / Sinistar tunables.

**Piece** — Two distinct meanings:
1. **Sinistar piece** — a skull fragment carried by workers during
   assembly. Also the score-able entity if the player shoots one
   in transit.
2. **Sinistar HP** — `tunables.yaml#pieces_required = 4`, the number of
   sinibomb hits to kill a fully-assembled Sinistar. The original code
   uses "piece" for both.

**Plan** — A warrior's tactical mission within a squadron. Plans select
which speed table the warrior uses. See `05-ai.md`.

**Population growth** — The mechanic by which entity counts climb during
a wave as DTime advances. See `06-progression.md`.

**Richter** — The unit of planetoid vibration. 0 = stable, 96 = shatter.
See `tunables.yaml#vibration_max`.

**Roar** — Sinistar's iconic non-verbal vocalization. See `speech.yaml#roar`.

**Scanner** — The radar panel showing entity positions across the sector.
See `01-world-model.md`.

**Sector** — One unit of progression (one "level"). Won by killing Sinistar.
See `06-progression.md`.

**Sinibomb** — The only weapon that damages Sinistar. Player carries up to 20.
See `02-entities.md#Sinibomb`.

**Squadron** — A formation of 1–5 warriors flying together. See
`05-ai.md#Squadron formation`.

**STBL\*** — Original assembly-source naming convention for speed tables
(`STBLWORK`, `STBLW0`, etc.). Captured in `speed-tables.yaml`.

**Stroking the watchdog** — The original code's term for the periodic
write that resets the hardware watchdog timer. **Hardware artifact**, out
of spec scope.

**Survivors Today** — The session-only RAM-backed high-score table.
5 entries. Seed 10,000. Resets on power cycle.

**Swarm** — A periodic AI event where workers and warriors converge on a
target. Probability `tunables.yaml#swarm_probability`.

**Tail (mode)** — A worker / warrior AI state where the entity follows
another in formation.

**Tail (effect)** — A separate optional visual effect (the SAMTAIL mod) where
the player ship draws a flame trail. Not canonical.

**Tick** — One simulation step. Original: 1/60 second.

**Toss** — Crystal ejection from a vibrating planetoid. See
`05-ai.md#Planetoid behavior`.

**TMS5220** — Texas Instruments speech synthesis chip family. The original's
speech is in this style (though the actual cabinet uses a separate speech
ROM with custom code by John Kotlarik). **Hardware artifact**, not spec.

**Warp** — The post-Sinistar-kill exit animation; player accelerates
off-screen, next sector loads. See `04-player.md#Ship warp`.

**Warp immunity** — Player invulnerability during warp-out. See
`03-physics-collision.md#Warp immunity`.

**Wave** — One position in the wave sequence (0–4). Determines initial
populations. See `06-progression.md`.
