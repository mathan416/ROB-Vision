# R.O.B. Vision virtual system contract

R.O.B. is a virtual character and accessory model. The UNO Q runs the controller and optional camera decoder; a laptop, iPad, or phone renders the robot and pieces. There are no physical arms, gyros, trays, blocks, or motors to build. RetroPie remains the game host.

## What is running

The UNO Q App Lab app serves the dashboard, owns virtual game state, receives authenticated RetroPie game-launch events, and sends snapshots to browsers. `retropie.local` has runcommand launch/exit hooks, a paired Linux virtual Controller 2 receiver, and a frame link for the two supported games. Gyromite red and blue gate controls were verified in Game A. The attached Kiyo Pro delivers about 60 fps at 640×480; live camera movement decoding was intermittent. In interactive Stack-Up Direct mode, the frame link decoded CLOSE and DOWN and updated the virtual model.

## Game rules in the model

Gyromite has two virtual gyros, holders, a spinner, and red/blue pads. A spinning gyro on a pad presses its gate; R.O.B. can also hold an unspun gyro on a pad. Moving, lifting, or spin expiry releases that pad. Each gyro has an illustrative 55-second spin clock. Fast Gates gives an immediate, 60-second maximum manual hold with camera capture stopped. The UNO Q's pad state is polled over LAN by RetroPie and applied to Controller 2. The browser does not decide button state independently.

Stack-Up has five colored blocks, five trays, six height levels, an arm station, and a shared grip. All five start on Tray 3 in the current live model. A lower grip carries the contacted block and all blocks above it as one ordered segment. Invalid moves are rejected without changing the stack. The original game's Direct, Memory, and Bingo modes send the same six movement commands; R.O.B. Vision does not yet initialize their different historical starting layouts or report scoring. Stack-Up does not use the Gyromite Controller 2 gate path.

## Browser and camera behavior

Mission shows the animated robot, accessory views, Game Table, Pose Preview, System Vitals, and activity. Setup has pairing, camera framing, Test-mode light acknowledgement, and manual game checks. A `file://` page is a local preview; use `http://arduiain.local/dashboard/` for UNO Q state. The static demo may run when RetroPie is paired but no game is active. A live game stops the demo and takes authority.

The camera capture code requests 60 fps and samples the central 60% by default. A complete recognized flash command changes the model; Test-mode flashing only animates R.O.B.'s red status light. A missing or uncertain command does nothing. When the RetroPie frame link is active, commands come from the emulator's rendered NES frames and camera movement decoding pauses, while camera preview and Test detection remain available. The service knows neither Hector's location nor Stack-Up scoring.

## Failure and reset

Game exit, unknown game, link loss, missing RetroArch, and stale receiver data release Gyromite's buttons. Browser reload recovers the controller snapshot. **Home** reinitializes the selected game. Live **Emergency Stop** stops capture and clears game selection; the preview version only cancels its local script. Setup **Reset & Reconnect** retries camera capture in software. USB hub recovery requires separately installed UNO Q host helpers and is not triggered by that button.

See the [technical architecture](TECHNICAL_ARCHITECTURE.md) for exact runtime paths and [configuration reference](CONFIGURATION_REFERENCE.md) for defaults.
