# R.O.B. Vision troubleshooting

If RetroPie's EmulationStation exits with an InputManager joystick assertion, return to its shell and rerun the console installer with EmulationStation closed. The installer checks module compatibility before restarting the virtual controller.

For installation failures, check the prerequisite or unsupported-device message from the single release command, then rerun that same command. The archive checksum must pass before the installer changes the device. After removing a console in Setup, rerun its command with `--pair`.

First check which page is open: use the UNO Q installer’s device-specific `.local` or LAN IP dashboard link for live state. A `file://` page or a simple static web server shows the independent preview. If `.local` does not resolve on a device, use the printed IP link on the same LAN and check Avahi on the UNO Q.

| Symptom | Check |
| --- | --- |
| App does not start, port 8766 in use | Stop VirtualGlove or the separate `rob-vision.service`; App Lab and that service cannot both bind the port. |
| `GYROMITE / CONNECTED` but no robot movement | Check the active console's **ONLINE** indicator and **GAME FRAMES LINKED** separately. If the latter is absent, restart the game with its R.O.B. Vision core. Check Mission's Activity Feed for decoded or blocked actions. |
| Console is online but no game is selected | A receiver can be online with no active game. Launch a registered ROM; then reload Mission if needed. |
| Test light never blinks | Enter the game's Test mode and confirm **GAME FRAMES LINKED** with the correct game selected. The light responds automatically to linked game frames. A red-light preview is only an animation demonstration. |
| Movement command is missed | Confirm **GAME FRAMES LINKED** and the correct game is selected. On RetroPie, choose `lr-robvision-fceumm` or `lr-robvision-nestopia`; on Batocera, launch the registered ROM with its installed R.O.B. Vision wrapper. Check the Activity Feed for a decoded command or a model move blocked by height, grip, or station. |
| Red/blue gate does not move | Confirm Gyromite is the active RetroArch game, Setup **Check Link** is online, and RetroArch port 2 is configured. Inspect the game screen during an isolated color hold. |
| A physical gamepad does not control the game | Try another connected gamepad. The one in your hands may be assigned to Player 2 while another is Player 1. In Setup > Controller Router, check the assignments, move the intended pad to the right player if needed, and relaunch the game. |
| A wireless controller falls asleep or wakes during a game | On RetroPie, a known Controller Router hotplug issue can shift RetroArch's numbered device slots. The game may stop receiving a physical pad even though the pad reconnects and its saved player assignment is still correct. Turn on the controllers you plan to use before launching a game. If one sleeps or wakes during play and input fails, exit and relaunch the game after it reconnects. In RetroArch, Port 1 should show **VirtualGlove Merged Player 1**; a different merged player indicates the shifted slot. A routing fix is pending. |
| Fast Gates vanished | They show only in live Gyromite. |
| Gate remains down | Select **Release Both**; a hold also expires at 60 seconds. The receiver releases on game exit or stale network data. |
| Stack-Up block does not move | Review current station, height, gripper, carried group, and destination capacity; invalid moves leave the stack intact and appear in activity. |
| Demo does not start | Exit the running game first. Demo mode works when paired and idle; **Home** resets it. |
| Browser shows stale scene | Reload for a fresh `/api/state` snapshot. A local preview cannot show UNO Q state. |

On RetroPie, check `rob-vision-controller2.service`, runcommand, and the ROM basename. On Batocera, check `ROBVision`, the per-ROM core, and the ROM basename. Linux `/dev/input/jsN` may differ from RetroArch's pad index. Check Setup > Controller Router for the saved player assignment; Router resolves the active pad indexes. Exclude credentials and ROM files from bug reports.
