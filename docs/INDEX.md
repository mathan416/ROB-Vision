# R.O.B. Vision documentation

[Latest release review](RELEASE_REVIEW_2026-09-25.md) records the code cleanup, local checks, and live validation still needed before a general release.

**Project scope:** a virtual R.O.B. driven by an Arduino UNO Q. The game runs on RetroPie; its rendered NES frames carry complete R.O.B. commands to the UNO Q. A browser on a laptop, iPad, or phone shows R.O.B. and the pieces; Gyromite virtual button states return to the game host over LAN. No physical robot or game pieces are planned. Both games' six commands were decoded during live Direct play, and Gyromite's gate controls were tested in Game A.

Printable editions: [User Guide](../output/pdf/R.O.B.-Vision-User-Guide.pdf), [Technical Reference](../output/pdf/R.O.B.-Vision-Technical-Reference.pdf), [Matrix Display Guide](../output/pdf/R.O.B.-Vision-Matrix-Display-Guide.pdf), and [Quick Reference](../output/pdf/R.O.B.-Vision-Quick-Reference.pdf).

## Start here

| Reader | Guide | What it covers |
| --- | --- | --- |
| Everyone | [Built-in Help center](../dashboard/help.html) | Searchable setup, play, controls, indicators, and troubleshooting inside the dashboard. |
| Everyone | [Project README](../README.md) | Scope, preview, and document links. |
| Everyone | [Virtual system contract](VIRTUAL_SYSTEM.md) | UNO Q, browser, virtual pieces, and game-link responsibilities. |
| Player | [User guide](USER_GUIDE.md) | Live controls, preview, and current limitations. |
| Player and installer | [Setup guide](SETUP_GUIDE.md) | Pairing, frame-link status, Test mode, and manual checks. |
| Player and installer | [UNO Q matrix display design](UNO_Q_MATRIX_DISPLAY.md) | Implemented matrix software and pending visual checks. |
| Player | [Gameplay guide](GAMEPLAY_GUIDE.md) | Gyromite, Stack-Up, holders, spin, and virtual button rules. |
| Player | [Quick reference](QUICK_REFERENCE.md) | Controls and indicators at a glance. |
| Installer | [Installation guide](INSTALLATION_GUIDE.md) | Installed UNO Q/RetroPie frame-link setup. |
| Developer | [Technical architecture](TECHNICAL_ARCHITECTURE.md) | State, commands, return path, and failure behavior. |
| Developer | [Configuration reference](CONFIGURATION_REFERENCE.md) | Code defaults, deployed settings, and calibration. |
| Tester | [Verification plan](VERIFICATION_PLAN.md) | Evidence before claiming a connected game works. |
| Everyone | [Troubleshooting](TROUBLESHOOTING.md) | Live and preview diagnostics. |

## Research and design references

- [Optical input](optical-input.md) and [ROM signal analysis](ROM_SIGNAL_ANALYSIS.md): flashes, timing, and command decoding.
- [Kiyo Pro row test](KIYO_PRO_ROW_TEST_2026-09-25.md): archived camera research; no longer part of the runtime.
- [Game identification](GAME_IDENTIFICATION.md): exact RetroPie launch-name matching.
- [Network architecture](network-architecture.md): virtual Controller 2 return path over Wi-Fi or Ethernet.
- [Dashboard design](DASHBOARD_DESIGN.md): robot art, accessory layout, and live state.
- [Gyromite manual notes](GYROMITE_MANUAL_NOTES.md), [Stack-Up manual notes](STACK_UP_MANUAL_NOTES.md), and [historical manual notes](HISTORICAL_MANUAL_NOTES.md): original behavior and game modes.
- [UNO Q setup](HARDWARE_BUILD_GUIDE.md) and [parts plan](parts-plan.md): controller, power, and network hardware only.
- [UNO Q host helpers](../deploy/uno-q/README.md) and [RetroPie deployment](../deploy/retropie/README.md): installed and optional system services.
- [Unattended engineering test report](UNATTENDED_TEST_REPORT_2026-09-24.md): synthetic optical and model evidence.
- [Live optical test report](LIVE_OPTICAL_TEST_2026-09-25.md): archived camera research; no longer part of the runtime.
- [Game-frame link report](FRAME_LINK_TEST_2026-09-25.md): live per-ROM frame decoding and model actions.
- [Nestopia frame-link report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md): second NES core, isolated game-frame checks, and remaining live validation.
- [Safety and security](SAFETY_AND_SECURITY.md), [third-party components](THIRD_PARTY_COMPONENTS.md), and [changelog](CHANGELOG.md).

The UNO Q app, RetroPie frame link, and Gyromite return path are running. All six frame command types in both games have been observed; longer unattended gameplay and Stack-Up Memory/Bingo remain to be validated. Historical manuals explain the original physical toy; this project renders those mechanics virtually.
