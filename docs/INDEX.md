# R.O.B. Vision documentation

[Current release review](RELEASE_REVIEW_2026-09-28.md) records the development review and remaining release gates. [Version 0.1.7 release notes](RELEASE_NOTES_0.1.7.md) describe that published stable release. The [0.1.6 notes](RELEASE_NOTES_0.1.6.md), [0.1.5 notes](RELEASE_NOTES_0.1.5.md), [0.1.4 notes](RELEASE_NOTES_0.1.4.md), [0.1.3 notes](RELEASE_NOTES_0.1.3.md), [0.1.2 notes](RELEASE_NOTES_0.1.2.md), [0.1.1 notes](RELEASE_NOTES_0.1.1.md), [0.1.0 notes](RELEASE_NOTES_0.1.0.md), and [dated engineering review](RELEASE_REVIEW_2026-09-25.md) remain available.

**Project scope:** a virtual R.O.B. driven by an Arduino UNO Q. The game runs on RetroPie or Batocera; its rendered NES frames carry complete R.O.B. commands to the UNO Q. A browser on a laptop, iPad, or phone shows R.O.B. and the pieces; Gyromite virtual button states return to the game host over LAN. Both games' six commands were decoded during live Direct play, and Gyromite's gate controls were tested in Game A.

Printable editions: [User Guide](../output/pdf/R.O.B.-Vision-User-Guide.pdf), [Installation & Setup](../output/pdf/R.O.B.-Vision-Installation-and-Setup.pdf), [Game Manual](../output/pdf/R.O.B.-Vision-Game-Manual.pdf), [Buddy newspaper Episode 1](../output/pdf/Buddy-Big-Wide-Window-Episode-1.pdf), [Buddy newspaper Episode 2](../output/pdf/Buddy-Big-Wide-Window-Episode-2.pdf), [Buddy newspaper Episode 3](../output/pdf/Buddy-Big-Wide-Window-Episode-3.pdf), [Technical Reference](../output/pdf/R.O.B.-Vision-Technical-Reference.pdf), [Technical Test Results](../output/pdf/R.O.B.-Vision-Technical-Test-Results.pdf), [Engineering Journey](../output/pdf/R.O.B.-Vision-Engineering-Journey.pdf), [Matrix Display Guide](../output/pdf/R.O.B.-Vision-Matrix-Display-Guide.pdf), and [Quick Reference](../output/pdf/R.O.B.-Vision-Quick-Reference.pdf).

The Technical Reference is generated from one cohesive [technical source](TECHNICAL_ARCHITECTURE.md). It covers current architecture, ROM-derived frame protocol, game identity, virtual model, Controller 2 return path, pairing, platform installation, recovery, and verified limits. Dated test reports and earlier camera research remain as separate evidence below.

## Start here

| Reader | Guide | What it covers |
| --- | --- | --- |
| Everyone | [Built-in Help center](../dashboard/help.html) | Searchable setup, play, controls, indicators, and troubleshooting inside the dashboard. |
| Everyone | [Project README](../README.md) | Scope, preview, and document links. |
| Everyone | [Meet Buddy](MEET_BUDDY.md) | Illustrated story chapter used in the printable User Guide. |
| Everyone | [Buddy & the Big Wide Window](BUDDY_ADVENTURE.md) | Three full-page newspaper episodes and printable PDFs. |
| Everyone | [Virtual system contract](VIRTUAL_SYSTEM.md) | UNO Q, browser, virtual pieces, and game-link responsibilities. |
| Player | [User guide](USER_GUIDE.md) | Live controls, preview, and current limitations. |
| Player and installer | [Setup guide](SETUP_GUIDE.md) | Pairing, frame-link status, Test mode, and manual checks. |
| Player and installer | [UNO Q matrix display guide](UNO_Q_MATRIX_DISPLAY.md) | What Buddy's hourglass, eyes, game marks, Test light, and pairing cue mean. |
| Player | [Gameplay guide](GAMEPLAY_GUIDE.md) | Gyromite, Stack-Up, holders, spin, and virtual button rules. |
| Player | [Game manual](GAME_MANUAL.md) | Printable game rules, live controls, and recovery for both games. |
| Player | [Quick reference](QUICK_REFERENCE.md) | Controls and indicators at a glance. |
| Installer | [Installation guide](INSTALLATION_GUIDE.md) | One command per device, browser pairing, upgrades, and supported hardware. |
| Installer | [Installation & Setup](INSTALLATION_AND_SETUP.md) | Standalone printable path from prerequisites to first game check. |
| Developer | [Technical reference source](TECHNICAL_ARCHITECTURE.md) | Complete current implementation and evidence boundaries. |
| Developer and tester | [Technical test results](TEST_RESULTS_TECHNICAL.md) | Consolidated optical, Kiyo Pro row, FCEUmm, Nestopia, and gate-return measurements. |
| Everyone | [Engineering journey](ENGINEERING_JOURNEY.md) | How camera testing led to the verified libretro frame link. |
| Developer | [Configuration reference](CONFIGURATION_REFERENCE.md) | Code defaults, deployed settings, and calibration. |
| Tester | [Verification plan](VERIFICATION_PLAN.md) | Evidence before claiming a connected game works. |
| Everyone | [Controller Router](CONTROLLER_ROUTER.md) | Player assignments, input tests, and recovery. |
| Everyone | [Troubleshooting](TROUBLESHOOTING.md) | Live and preview diagnostics. |

## Research and design references

- [Buddy story brief](BUDDY_STORY.md): internal character and interface design notes.
- [Documentation standard](DOCUMENTATION_STANDARD.md): editorial rules for player Help, manuals, and engineering reference.
- [Optical input](optical-input.md) and [ROM signal analysis](ROM_SIGNAL_ANALYSIS.md): flashes, timing, and command decoding.
- [Kiyo Pro row test](KIYO_PRO_ROW_TEST_2026-09-25.md): archived camera research; no longer part of the runtime.
- [Game identification](GAME_IDENTIFICATION.md): RetroPie launch-hook research and exact ROM-name matching.
- [Technical architecture](TECHNICAL_ARCHITECTURE.md): network pairing, console identity, and virtual Controller 2 return path.
- [Dashboard design](DASHBOARD_DESIGN.md): robot art, accessory layout, and live state.
- [Gyromite manual notes](GYROMITE_MANUAL_NOTES.md), [Stack-Up manual notes](STACK_UP_MANUAL_NOTES.md), and [historical manual notes](HISTORICAL_MANUAL_NOTES.md): original behavior and game modes.
- [UNO Q hardware setup](HARDWARE_BUILD_GUIDE.md): required devices, power, and network connection.
- [UNO Q host helpers](../deploy/uno-q/README.md), [RetroPie deployment](../deploy/retropie/README.md), and [Batocera deployment](../deploy/batocera/README.md): installed and optional system services.
- [Unattended engineering test report](UNATTENDED_TEST_REPORT_2026-09-24.md): synthetic optical and model evidence.
- [Live optical test report](LIVE_OPTICAL_TEST_2026-09-25.md): archived camera research; no longer part of the runtime.
- [Game-frame link report](FRAME_LINK_TEST_2026-09-25.md): live per-ROM frame decoding and model actions.
- [Nestopia frame-link report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md): second NES core, isolated game-frame checks, and remaining live validation.
- [Safety and security](SAFETY_AND_SECURITY.md), [third-party components](THIRD_PARTY_COMPONENTS.md), and [changelog](CHANGELOG.md).

The UNO Q app, console frame link, and Gyromite return path are running. All six frame command types in both games have been observed; longer unattended gameplay and Stack-Up Memory/Bingo remain to be validated. Historical manuals explain the original accessories that inspired the virtual model.
