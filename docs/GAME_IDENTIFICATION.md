# Game identification from RetroPie launch events

**Status: installed on the dedicated `retropie.local` test machine.** The real Gyromite launch selected the game on the UNO Q. Controlled start/end calls selected and cleared both games; the real exit remains to be observed. The game still flashes commands for the camera to decode. Launch identification supplies context and does not replace optical input.

## Decision

Use the same *approach* as VirtualGlove: a small RetroPie runcommand launch/end hook sends the game identity. On the dedicated test machine there were no existing custom hooks, so [launch](../deploy/retropie/runcommand-onlaunch.sh) and [end](../deploy/retropie/runcommand-onend.sh) scripts were installed. At launch, RetroPie supplies system, emulator, ROM path, and command. Match the **exact ROM basename including `.nes`, `.zip`, or `.7z`**, case-insensitively, against an explicit registry. At exit, clear the active game. On another machine, merge with any existing hook rather than overwriting it.

Only `nes` and `famicom` are eligible. An unregistered filename or other system resolves to idle, not a guessed game. A changed archive filename needs an explicit registry entry. This avoids recognizing an unrelated game merely because its name contains “Gyromite” or “Stack-Up.”

The checked-in [registry](../config/games.json) covers the user's `Gyromite (World)` and `Stack-Up (World)` `.7z` and `.zip` files plus their named `.nes` members. A read-only inspection of the supplied archives on 24 September 2026 found one 40,976-byte `.nes` member per archive. For each game, its `.zip` and `.7z` members had identical bytes. No ROM bytes, extracted files, or archive copies were added to R.O.B. Vision.

## Resolver and live check

The [resolver](../tools/identify_game.py) accepts the same four launch arguments used by RetroPie and prints a small JSON event. The [sender](../tools/notify_game.py) authenticates to the UNO Q using the token file and sends the event without blocking game launch on failure. On 24 September 2026, a real EmulationStation Gyromite launch used the `.7z` archive and selected `gyromite` on the UNO Q. Synthetic calls of the installed hooks selected and cleared both games. A real exit has not yet been observed.

```sh
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Gyromite (World).zip" ""
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Stack-Up (World).7z" ""
python3 tools/identify_game.py end
```

The first two calls identify `gyromite` and `stack_up`; the last returns `idle`. The ROM argument is the **launched filename** reported by RetroPie, not the inner `.nes` member of an archive unless RetroPie actually launches that extracted file.

## Current cabinet-to-robot path

```text
RetroPie runcommand start/end
  → exact local registry match
  → authenticated LAN game-state event
  → UNO Q selects and displays game/accessory context
  → optical test + virtual accessory profile checks
  → READY for validated screen-flash commands
```

The current sender transmits system, ROM path, and launch/exit event over authenticated HTTP with a short timeout. Session IDs, sequence numbers, retries, and a lease timeout remain future reliability work. A successful launch event is not proof that the camera is calibrated or ready.

The virtual robot should display `GYROMITE`, `STACK-UP`, or `UNKNOWN GAME` along with the source of identification. It should never animate a game command merely because a launch event arrived. An authenticated hook event selects the expected game profile, while the camera independently validates actual optical commands. If the two disagree, show a mismatch and refuse game-driven virtual actions until the operator resolves it. Manual game selection may support a non-RetroPie source, but must be explicit and pass the same optical and virtual-state checks.

Gyromite's paired tray-to-Controller-2 return path remains separate from this launch notification. Stack-Up needs no gyro-style button return in its documented modes. Both games may use the Wi-Fi/Ethernet launch event for context while receiving their movement commands through the camera.

## Acceptance checks before installation

1. Simulate all six registered archive/member basenames, an unrelated NES ROM, and another system; verify only intended games match.
2. Launch both archive formats through the real RetroPie UI and record the **actual** system and ROM argument; adjust the registry only from that observation.
3. Verify start, exit, unknown game, back-to-back game launches, missed acknowledgement, and sender/robot restart. No stale game may stay armed.
4. Confirm all existing cabinet runcommand actions still execute in their original order and that hook failure never prevents the game from starting.
5. Compare the launch identity with camera-observed Test/Direct flashes. Only matching, calibrated signals may enable future game-specific virtual commands.

See [network architecture](network-architecture.md), [optical input](optical-input.md), [configuration](CONFIGURATION_REFERENCE.md), and [verification plan](VERIFICATION_PLAN.md).
