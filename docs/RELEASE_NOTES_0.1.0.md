# R.O.B. Vision 0.1.0

R.O.B. Vision is a virtual robot companion for Gyromite and Stack-Up. The UNO Q owns the game-piece state and serves the Mission, Setup, and Help pages. RetroPie and supported Batocera systems pass NES frame signals to the UNO Q through FCEUmm or Nestopia wrappers. The frame link needs no camera.

## New in 0.1.0

- One versioned, SHA-256-checked install command on the UNO Q and one common console command on RetroPie or Batocera. Neither device needs a Git checkout or SSH source transfer.
- First-time console pairing opens during installation. RetroPie updates stop the receiver before replacing its modules and require EmulationStation to be closed during virtual joystick restart. The code and fingerprint go into UNO Q Setup; pairing starts the receiver and configures Gyromite's virtual Controller 2 without another console command. Both console installers install its RetroArch controller profile on clean systems.
- Batocera hardware/version preflight and automatic EmulationStation suspend/resume during receiver upgrades. The validated Batocera target is 43.1 x86_64; other boards are reported clearly and are not claimed as supported.
- Batocera service startup waits for VirtualGlove's native core when that receiver is enabled, preserving both Libretro core overlays after reboot. The UNO Q App Lab apps still run one at a time because each serves port 80.
- Updated built-in Help, user and technical guides, four PDF manuals, MIT license, provenance notes, and release checksums.

## Supported setup

Arduino UNO Q with App Lab; standard RetroPie with the `pi` account and installed FCEUmm and/or Nestopia; Batocera 43.1 x86_64 with the included wrappers. Bring your own legally obtained Gyromite and Stack-Up ROMs. The release contains no ROMs or stock emulator cores.

## Current limits

The virtual model responds to the game's light commands but cannot read Hector's position, score, or Stack-Up's target pattern. Stack-Up Direct movement is supported; longer Memory and Bingo sessions require further live validation. Gyromite's blue gate return under Nestopia passed live Game A checks on Batocera and RetroPie after the Player 2 gamepad fix. Demo mode works while a console is paired and idle.

R.O.B. Vision is an independent project and is not affiliated with or endorsed by Nintendo. See [Third-party components and rights](THIRD_PARTY_COMPONENTS.md).
