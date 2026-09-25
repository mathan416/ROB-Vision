# R.O.B. Vision build brief

## Objective

Create a lively virtual R.O.B. for Gyromite and Stack-Up, driven by an Arduino UNO Q. The cabinet runs the game on a modern display. The UNO Q camera watches optical flashes, updates a virtual R.O.B. and all accessory pieces, and serves an animated dashboard to a laptop, iPad, or phone. Gyromite virtual pad states return to the game host over Wi-Fi or Ethernet as Controller 2 input. No physical R.O.B., motors, gyros, spinner, trays, blocks, or grippers are planned.

## Player experience

The large screen view keeps R.O.B.'s friendly face, two opposing hands, moving head, and accessory table visible together. Gyromite shows two holders, one spinner, two gyros, and red/blue pads. Stack-Up shows five trays and five colored blocks. Every accepted optical command changes the UNO Q's virtual state and generates an ordered event; all dashboard clients animate from that state. Camera diagnostics are secondary to the R.O.B. view.

The current browser demo is a design study. Its Gyromite sequence demonstrates an unspun one-gate press, a two-gyro relay, spin-down and one re-spin recovery each, then a return to holders and a stable stop. Stack-Up moves red alone from Tray 3 to Tray 4, then carries blue and white together to Tray 2. Its local command controls use the same virtual stack model. The demo has no camera or game connection.

## Planned software blocks

1. Exact configured RetroPie launch-name hook for game identity, with clear state on exit.
2. Timestamped UNO Q camera capture and optical command decoder for both games.
3. UNO Q virtual action controller and piece-state reducer with bounded pose and valid transfers.
4. Paired Gyromite LAN sender and game-host virtual Controller 2 receiver with timeout release.
5. Browser snapshot/event stream for laptop, tablet, and phone.
6. Diagnostic replay and acceptance tests against user-supplied ROMs and actual display behavior.

## Milestones

| Stage | Evidence |
| --- | --- |
| Browser preview | Art, finite demos, controls, and virtual state visibly agree. |
| Optical bench | Test and Direct flashes decoded from intended LCD/OLED with no false idle command. |
| UNO Q virtual controller | Same command causes one valid pose/piece change and ordered browser event. |
| Gyromite return path | Red/blue virtual pad mapping verified in game, with release on exit/disconnect. |
| Connected game play | Gyromite and Stack-Up sessions work end to end with logs and recovery diagnostics. |

The [virtual system contract](VIRTUAL_SYSTEM.md) and [technical architecture](TECHNICAL_ARCHITECTURE.md) are authoritative for scope and runtime behavior.
