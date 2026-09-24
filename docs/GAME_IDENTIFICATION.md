# Game identification from RetroPie launch events

**Status: local resolver prototype; no cabinet hook, network sender, or robot receiver is installed.** The game still flashes commands for the head camera to decode. Launch identification supplies context and the correct accessory guide; it does not authorize motion or replace the optical input.

## Decision

Use the same *approach* as VirtualGlove: append a small call to RetroPie's existing `runcommand-onstart.sh` and `runcommand-onend.sh` chain. At launch, RetroPie supplies system, emulator, ROM path, and command. Match the **exact ROM basename including `.nes`, `.zip`, or `.7z`**, case-insensitively, against an explicit registry. At exit, clear the active game. Preserve the cabinet's existing VirtualGlove, controller, RGB, and trackball hooks; do not replace their scripts.

Only `nes` and `famicom` are eligible. An unregistered filename or other system resolves to idle, not a guessed game. A changed archive filename needs an explicit registry entry. This avoids recognizing an unrelated game merely because its name contains “Gyromite” or “Stack-Up.”

The checked-in [registry](../config/games.json) covers the user's `Gyromite (World)` and `Stack-Up (World)` `.7z` and `.zip` files plus their named `.nes` members. A read-only inspection of the supplied archives on 24 September 2026 found one 40,976-byte `.nes` member per archive. For each game, its `.zip` and `.7z` members had identical bytes. No ROM bytes, extracted files, or archive copies were added to R.O.B. Vision.

## Current local check

The [resolver](../tools/identify_game.py) accepts the same four launch arguments used by RetroPie and prints a small JSON event. It does **not** send that event over the LAN or edit a runcommand hook.

```sh
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Gyromite (World).zip" ""
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Stack-Up (World).7z" ""
python3 tools/identify_game.py end
```

The first two calls identify `gyromite` and `stack_up`; the last returns `idle`. The ROM argument is the **launched filename** reported by RetroPie, not the inner `.nes` member of an archive unless RetroPie actually launches that extracted file.

## Planned cabinet-to-robot contract

```text
RetroPie runcommand start/end
  → exact local registry match
  → authenticated, ordered LAN game-state event
  → UNO Q acknowledges and displays game/accessory context
  → optical test + virtual accessory profile checks
  → READY for validated screen-flash commands
```

The sender should include a session ID, monotonic sequence, system, sanitized ROM basename, game ID or `idle`, and launch/exit event type. It should retry for an authenticated acknowledgement without blocking the game launch. The robot should ignore duplicate or stale events, clear game readiness on an exit or unknown title, and clear stale game context after a bounded heartbeat/lease timeout. A queued acknowledgement is not proof that the robot is calibrated or ready.

The virtual robot should display `GYROMITE`, `STACK-UP`, or `UNKNOWN GAME` along with the source of identification. It should never animate a game command merely because a launch event arrived. An authenticated hook event selects the expected game profile, while the camera independently validates actual optical commands. If the two disagree, show a mismatch and refuse game-driven virtual actions until the operator resolves it. Manual game selection may support a non-RetroPie source, but must be explicit and pass the same optical and virtual-state checks.

Gyromite's paired tray-to-Controller-2 return path remains separate from this launch notification. Stack-Up needs no gyro-style button return in its documented modes. Both games may use the Wi-Fi/Ethernet launch event for context while receiving their movement commands through the camera.

## Acceptance checks before installation

1. Simulate all six registered archive/member basenames, an unrelated NES ROM, and another system; verify only intended games match.
2. Launch both archive formats through the real RetroPie UI and record the **actual** system and ROM argument; adjust the registry only from that observation.
3. Verify start, exit, unknown game, back-to-back game launches, missed acknowledgement, and sender/robot restart. No stale game may stay armed.
4. Confirm all existing cabinet runcommand actions still execute in their original order and that hook failure never prevents the game from starting.
5. Compare the launch identity with camera-observed Test/Direct flashes. Only matching, calibrated signals may enable future game-specific virtual commands.

See [network architecture](network-architecture.md), [optical input](optical-input.md), [configuration](CONFIGURATION_REFERENCE.md), and [verification plan](VERIFICATION_PLAN.md).
