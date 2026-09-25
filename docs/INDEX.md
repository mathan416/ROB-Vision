# R.O.B. Vision documentation

**Project scope:** a virtual R.O.B. driven by an Arduino UNO Q. The game runs on a cabinet screen; the UNO Q camera will read its flashes; a browser on a laptop, iPad, or phone shows R.O.B. and the pieces; Gyromite virtual button states return to the game host over LAN. No physical robot or game pieces are planned. The UNO Q dashboard, RetroPie launch hooks, and both Gyromite gate controls have been tested. Camera capture with the intended hardware remains to be verified.

Printable editions: [User Guide](../output/pdf/R.O.B.-Vision-User-Guide.pdf), [Technical Reference](../output/pdf/R.O.B.-Vision-Technical-Reference.pdf), and [Quick Reference](../output/pdf/R.O.B.-Vision-Quick-Reference.pdf).

## Start here

| Reader | Guide | What it covers |
| --- | --- | --- |
| Everyone | [Project README](../README.md) | Scope, preview, and document links. |
| Everyone | [Virtual system contract](VIRTUAL_SYSTEM.md) | UNO Q, browser, virtual pieces, and game-link responsibilities. |
| Player | [User guide](USER_GUIDE.md) | Live controls, preview, and current limitations. |
| Player and installer | [Setup guide](SETUP_GUIDE.md) | Pairing, camera placement, Test mode, and manual checks. |
| Player and installer | [UNO Q matrix display design](UNO_Q_MATRIX_DISPLAY.md) | Implemented matrix software and pending visual checks. |
| Player | [Gameplay guide](GAMEPLAY_GUIDE.md) | Gyromite, Stack-Up, holders, spin, and virtual button rules. |
| Player | [Quick reference](QUICK_REFERENCE.md) | Controls and indicators at a glance. |
| Installer | [Installation guide](INSTALLATION_GUIDE.md) | Installed UNO Q/RetroPie setup and camera commissioning. |
| Developer | [Technical architecture](TECHNICAL_ARCHITECTURE.md) | State, commands, return path, and failure behavior. |
| Developer | [Configuration reference](CONFIGURATION_REFERENCE.md) | Code defaults, deployed settings, and calibration. |
| Tester | [Verification plan](VERIFICATION_PLAN.md) | Evidence before claiming a connected game works. |
| Everyone | [Troubleshooting](TROUBLESHOOTING.md) | Live and preview diagnostics. |

## Research and design references

- [Optical input](optical-input.md) and [ROM signal analysis](ROM_SIGNAL_ANALYSIS.md): flashes, timing, and command decoding.
- [Game identification](GAME_IDENTIFICATION.md): exact RetroPie launch-name matching.
- [Network architecture](network-architecture.md): virtual Controller 2 return path over Wi-Fi or Ethernet.
- [Dashboard design](DASHBOARD_DESIGN.md): robot art, accessory layout, and live state.
- [Gyromite manual notes](GYROMITE_MANUAL_NOTES.md), [Stack-Up manual notes](STACK_UP_MANUAL_NOTES.md), and [historical manual notes](HISTORICAL_MANUAL_NOTES.md): original behavior and game modes.
- [UNO Q setup](HARDWARE_BUILD_GUIDE.md) and [parts plan](parts-plan.md): controller, camera, power, and optional network hardware only.
- [UNO Q host helpers](../deploy/uno-q/README.md) and [RetroPie deployment](../deploy/retropie/README.md): installed and optional system services.
- [Unattended engineering test report](UNATTENDED_TEST_REPORT_2026-09-24.md): synthetic optical and model evidence.
- [Safety and security](SAFETY_AND_SECURITY.md), [third-party components](THIRD_PARTY_COMPONENTS.md), and [changelog](CHANGELOG.md).

The UNO Q app and Gyromite return path are running. Camera/display decoding and full interactive Stack-Up play remain unverified. Historical manuals explain the original physical toy; this project renders those mechanics virtually.
