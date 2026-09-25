# R.O.B. Vision troubleshooting

First check which page is open: `http://arduiain.local/dashboard/` is live; a `file://` page or a simple static web server shows the independent preview.

| Symptom | Check |
| --- | --- |
| App does not start, port 8766 in use | Stop VirtualGlove or the separate `rob-vision.service`; App Lab and that service cannot both bind the port. |
| `GYROMITE / CONNECTED` but no robot movement | Check **RETROPIE ONLINE** and **GAME FRAMES LINKED** separately. If the latter is absent, restart the game so RetroPie loads the R.O.B. Vision core. Check Mission's Activity Feed for decoded or blocked actions. |
| RetroPie is online but no game is selected | A receiver can be online with no active game. Launch a registered ROM; then reload Mission if needed. |
| Test light never blinks | Enter the game's Test mode and confirm **GAME FRAMES LINKED** with the correct game selected. The light responds automatically to linked game frames. A red-light preview is only an animation demonstration. |
| Movement command is missed | On RetroPie, confirm **GAME FRAMES LINKED** and the correct game is selected. The frame link reads every rendered NES frame; check the Activity Feed for a decoded command or a model move blocked by height, grip, or station. |
| Red/blue gate does not move | Confirm Gyromite is the active RetroArch game, Setup **Check Link** is online, and RetroArch port 2 is configured. Inspect the game screen during an isolated color hold. |
| Fast Gates vanished | They show only in live Gyromite. |
| Gate remains down | Select **Release Both**; a hold also expires at 60 seconds. The receiver releases on game exit or stale network data. |
| Stack-Up block does not move | Review current station, height, gripper, carried group, and destination capacity; invalid moves leave the stack intact and appear in activity. |
| Demo does not start | Exit the running game first. Demo mode works when paired and idle; **Home** resets it. |
| Browser shows stale scene | Reload for a fresh `/api/state` snapshot. A local preview cannot show UNO Q state. |

On the dedicated RetroPie test setup, `systemctl status rob-vision-controller2.service` checks the root virtual-controller service. Inspect RetroPie's runcommand log and configured ROM basename if launch identity is missing. `/dev/input/js1` is expected for the virtual Controller 2 while the player's controller is generally `/dev/input/js0`. Keep tokens and ROM files out of bug reports.
