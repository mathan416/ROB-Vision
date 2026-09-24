# R.O.B. Vision technical architecture

**Status: local controller prototype plus browser simulation.** The UNO Q is the planned deployment target; R.O.B. and all accessories are virtual. The Python service now implements ROM-pattern decoding, optional OpenCV capture, virtual accessory state, and an HTTP dashboard connection. The camera and UNO Q have not been bench validated. Gyromite's LAN Controller 2 return path remains unimplemented. See the [virtual system contract](VIRTUAL_SYSTEM.md).

## Components and authority

| Component | Owns | Does not own |
| --- | --- | --- |
| Game display/emulator | Game rendering and optical flashes | R.O.B. Vision's virtual pose |
| Optional RetroPie launch hook | Exact configured game ID and launch/exit state | Motion commands or ROM-content proof |
| UNO Q camera decoder | Timestamped frames, flash region, complete-command validation | Virtual pad assertions from partial flashes |
| UNO Q mode adapter and virtual robot controller | One accepted action, bounded pose, gyro/disc state, virtual pad state, ordered events | Professor location or unobserved game outcome |
| UNO Q LAN sender | Fresh red/blue virtual Controller 2 states | Arbitrary emulator commands |
| Paired game-host receiver | Virtual Controller 2 button state and timeout release | Trusting stale or unpaired packets |
| Browser dashboard | Live R.O.B., pieces, controls, explanations, and history on laptop/iPad/phone | Independent game state or button authority |

The currently available dashboard substitutes a local scripted state machine for the UNO Q stream. Its `SIMULATION` status must remain visible until a real UNO Q session connects.

## Optical to virtual action

1. Gyromite or Stack-Up displays an optical command on the cabinet LCD/OLED.
2. The UNO Q timestamps camera frames, samples the calibrated flash region, and decodes one complete command. Ambiguous or partial messages are rejected.
3. The mode adapter interprets the primitive for the active game. Gyromite up/down spans two calibrated levels; Stack-Up up/down spans one, according to the [ROM analysis](ROM_SIGNAL_ANALYSIS.md).
4. The virtual controller accepts one command when ready, applies a bounded pose or grip change, and updates virtual object locations where the action legitimately changes them.
5. It publishes a versioned snapshot and ordered events over LAN. Browser clients animate from those states.
6. In Gyromite, the virtual pad reducer sends any changed red/blue state through the paired LAN return path. The receiver exposes the configured Controller 2 button mapping to the emulator.

A launch hook can select the correct game adapter from exact configured ROM filenames, following the [game identification design](GAME_IDENTIFICATION.md). It does not bypass camera calibration or supply optical motion commands. Unknown games leave the controller idle.

## Virtual Gyromite state

Track each gyro separately: `id`, `location`, `spin_phase`, `spin_started_at`, `spin_speed_or_estimate`, `held_by_robot`, and `upright`. Locations are `holder_a`, `holder_b`, `spinner`, `held`, `red_pad`, and `blue_pad`. The virtual spinner starts or restores spin; time and animation move a gyro through spinning, slowing, wobbling, and stopped phases. The browser demo uses a 55-second illustrative lifetime, not a measurement from original hardware.

The virtual red or blue pad is pressed when an upright spinning gyro occupies it, or when an unspun gyro is explicitly held down there by R.O.B. Moving, lifting, or tipping it releases the pad. Pad state is a deterministic output of the UNO Q's virtual model: there are no tray sensors. Both virtual buttons release on mode exit, game exit, session reset, sender timeout, or receiver timeout. A button transition and the corresponding visible state update must share one event sequence so the dashboard and game return path cannot silently disagree.

The [Gyromite booklet](https://www.digitpress.com/library/manuals/nes/gyromite.txt) says a single gate does not require a spinning gyro; holding an unspun one on its pad suffices. A spinning gyro frees R.O.B.'s hands to operate the other gate. A gyro no longer needed returns to its holder. Optical/player commands direct live play; the preview's scripted recovery is only a demonstration and must not be assumed to solve a level autonomously.

## Virtual Stack-Up state

The [browser stack model](../dashboard/stack-model.js) tracks five disc IDs, ordered contents of each of five trays, carried stack segment, station (1–5), height (six levels), and open/closed grippers. At the selected height, closing the grippers takes the contacted disc and all discs above it as one ordered segment; opening releases the full segment onto the target stack. A top-disc transfer is one special case. It validates height and station bounds, carried clearance, destination capacity, and conservation of all five discs before committing each command. Rejected actions leave state unchanged. This model currently drives the local scripted demo and manual buttons. The planned UNO Q service must own equivalent authoritative state. Memory mode requires a bounded plan for rapid commands; Bingo's simultaneous row-and-column no-command case must remain a no-op. Stack-Up's documented modes have no gyro-pad return path.

## State and event contract

The UNO Q session has `BOOT`, `CALIBRATING`, `READY`, `BUSY`, `PAUSED`, `FAULT`, and `EXITED` states. Events carry session ID, monotonic sequence, timestamp, game/mode, source (`optical`, `local`, or `hook`), accepted/rejected command, virtual pose, object state, virtual pad state, and game-link freshness. A reconnecting browser receives a snapshot before subsequent events. The UI shows commanded action, modeled result, and connection status separately. It never labels an unobserved game result as confirmed.

The virtual controller accepts semantic actions with bounded coordinates and valid object transitions. A second optical command while busy is rejected with a visible event by default; a bounded queue is allowed only after mode-specific timing tests. A complete duplicate transmission is a new event, not a continuation of the previous flash.

## Failure and reset behavior

| Condition | Controller behavior |
| --- | --- |
| Partial/unreadable flash | Reject; no virtual action. |
| Game exit or unknown title | Stop game-specific actions; release both Gyromite buttons. |
| LAN sender/receiver timeout | Release both virtual buttons; mark return path unavailable. |
| Browser disconnect | Preserve UNO Q state; reconnect from snapshot. |
| Impossible virtual transfer | Reject with diagnostic; do not mutate piece stacks or buttons. |
| Local demo Home/Stop | Cancel pending script and spin/recovery timers; release local virtual buttons. |

The dashboard's **Emergency Stop** is currently a local simulation cancel control. In this virtual design it is not a physical motor-power cutoff. The integration must protect optical input and paired LAN messages against stale, malformed, or unauthorized data; see [safety and security](SAFETY_AND_SECURITY.md) and [network architecture](network-architecture.md).

## Implementation map

Available: the standalone browser simulation; `controller/optical.py` for ROM-derived patterns; `controller/model.py` for virtual game state; `controller/service.py` for optional OpenCV capture and HTTP snapshots; `dashboard/live.js` for the browser connection; exact-name resolution and optional launch notification in `tools/`; and ROM analysis. Planned: measured UNO Q camera settings, ordered live event stream, paired Gyromite Controller 2 receiver, installer, and replay diagnostics. No pin map or motor firmware is required for the virtual R.O.B.
