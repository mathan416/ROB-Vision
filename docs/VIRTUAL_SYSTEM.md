# R.O.B. Vision virtual system contract

Buddy is a virtual character and accessory model. The UNO Q runs the controller; a laptop, iPad, or phone renders him and the game pieces. RetroPie or supported Batocera runs the game.

## What is running

The UNO Q App Lab app serves the dashboard, owns virtual game state, receives authenticated console game-launch events, and sends snapshots to browsers. The paired console has launch/exit hooks, a Linux virtual Controller 2 receiver, and a frame link for the two supported games. Only the active game's console may send its commands to the UNO Q. See the [release validation report](RELEASE_VALIDATION_0.1.0.md) for dated gameplay evidence.

## Game rules in the model

Gyromite has two virtual gyros, holders, a spinner, and red/blue pads. A spinning gyro on a pad presses its gate; R.O.B. can also hold an unspun gyro on a pad. Moving, lifting, or spin expiry releases that pad. Each gyro has an illustrative 55-second spin clock. Fast Gates gives an immediate, 60-second maximum manual hold. The UNO Q's pad state is polled over LAN by the active console and applied to Controller 2. The browser does not decide button state independently.

Stack-Up has five colored blocks, five trays, six height levels, an arm station, and a shared grip. All five start on Tray 3 in the current live model. A lower grip carries the contacted block and all blocks above it as one ordered segment. Invalid moves are rejected without changing the stack. The original game's Direct, Memory, and Bingo modes send the same six movement commands; R.O.B. Vision does not yet initialize their different historical starting layouts or report scoring. Stack-Up does not use the Gyromite Controller 2 gate path.

## Browser behavior

Mission shows the animated robot, accessory views, Game Table, Pose Preview, System Vitals, and activity. Setup has pairing, frame-link status, Test-mode light acknowledgement, and manual game checks. A `file://` page is a local preview; use `http://arduiain.local/dashboard/` for UNO Q state. The static demo may run when a console is paired but no game is active. A live game stops the demo and takes authority.

The console frame link reads rendered NES frames. A complete 13-frame command changes the model; Test-mode frames automatically animate R.O.B.'s red status light. Incomplete commands do nothing. The service knows neither Hector's location nor Stack-Up scoring.

## Failure and reset

Game exit, unknown game, link loss, missing RetroArch, and stale receiver data release Gyromite's buttons. Browser reload recovers the controller snapshot. **Home** reinitializes the selected game. Live **Emergency Stop** clears game selection and releases virtual pads; the preview version only cancels its local script.

See the [technical architecture](TECHNICAL_ARCHITECTURE.md) for exact runtime paths and [configuration reference](CONFIGURATION_REFERENCE.md) for defaults.
