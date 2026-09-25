# R.O.B. Vision build brief

## Objective and current state

R.O.B. Vision renders Nintendo's robotic companion and accessories as a virtual system controlled by an Arduino UNO Q. The game runs on RetroPie and a modern display; the UNO Q camera is intended to read its optical flashes. A laptop, iPad, or phone displays R.O.B. and the game table. Gyromite virtual pad states return over LAN as Controller 2 input. No physical robot or game accessories are built.

The UNO Q App Lab app, dashboard, matrix sketch, virtual models, ROM-derived decoder, launch/exit hooks, pairing, and RetroPie receiver are implemented. Gyromite red and blue gate responses were user-confirmed in Game A. The decoder has synthetic 30/60 fps stress results. The attached camera recognized both games' Test modes at about 60 fps, but movement commands did not decode. Stack-Up's virtual block flows and its live RetroArch Test, Direct, and Memory screens were reached; complete camera-driven Stack-Up play remains to be tested.

## Player experience

The main view animates R.O.B.'s connected arms, shared hands, moving head, gyros, and five colored Stack-Up blocks. Mission shows the Game Table beside Pose Preview and System Vitals. Setup provides pairing, camera framing, Test-mode light acknowledgement, and manual controls. Scripted demos remain available while paired but no game is active; a game launch selects the live scene.

## Remaining milestones

1. Attach a suitable camera to the UNO Q and confirm its real capture node and measured frame timing.
2. Validate Test and movement flashes from both games on the intended display, including idle false-trigger testing and Stack-Up Memory timing.
3. Run complete interactive Gyromite and Stack-Up sessions through the camera path; use an emulator hook only if camera sampling proves inadequate.
4. Verify multi-device dashboard behavior and each matrix indication visually on the physical UNO Q.

The [technical architecture](TECHNICAL_ARCHITECTURE.md), [configuration reference](CONFIGURATION_REFERENCE.md), and [verification plan](VERIFICATION_PLAN.md) describe the code and evidence.
