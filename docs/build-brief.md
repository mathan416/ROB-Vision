# R.O.B. Vision build brief

## Objective and current state

R.O.B. Vision renders Nintendo's robotic companion and accessories as a virtual system controlled by an Arduino UNO Q. The game runs on RetroPie and a modern display; a game-frame link reads its optical messages directly from rendered NES frames. The frame link also reports game Test signals. A laptop, iPad, or phone displays R.O.B. and the game table. Gyromite virtual pad states return over LAN as Controller 2 input. No physical robot or game accessories are built.

The UNO Q App Lab app, dashboard, matrix sketch, virtual models, ROM-derived decoder, launch/exit hooks, pairing, and RetroPie receiver are implemented. Gyromite red and blue gate responses were user-confirmed in Game A. The installed frame link decoded all six command types in both games during live Direct play. Stack-Up Memory and Bingo and long-session reliability remain to be measured.

## Player experience

The main view animates R.O.B.'s connected arms, shared hands, moving head, gyros, and five colored Stack-Up blocks. Mission shows the Game Table beside Pose Preview and System Vitals. Setup provides pairing, frame-link status, Test-mode light acknowledgement, and manual controls. Scripted demos remain available while paired but no game is active; a game launch selects the live scene.

## Remaining milestones

1. Run longer interactive sessions through the RetroPie frame link and measure missed and false commands, including Stack-Up Memory and Bingo.
2. Confirm live Test-mode indication through both supported frame-link cores.
3. Verify multi-device dashboard behavior and each matrix indication visually on the physical UNO Q.

The [technical architecture](TECHNICAL_ARCHITECTURE.md), [configuration reference](CONFIGURATION_REFERENCE.md), and [verification plan](VERIFICATION_PLAN.md) describe the code and evidence.
