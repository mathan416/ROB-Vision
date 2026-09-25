# Live optical test - 25 September 2026

## Setup

- R.O.B. Vision ran on the Arduino UNO Q at `arduiain.local`; RetroPie ran at `retropie.local` and sent authenticated game launch and exit events.
- A Razer Kiyo Pro connected to the UNO Q watched the modern display. It delivered approximately 59.8-60 frames per second at 640 x 480 MJPEG with HDR temporarily disabled.
- The first camera position used a tight normalized sampling region of `0.4,0.54,0.055,0.06`. After the display was centered in the camera image, the region moved to `0.4,0.30,0.055,0.06`. These coordinates are specific to this camera placement.
- The games were the user's supplied world ROM archives. No ROM is included in this repository.

## What happened

| Check | Live result | Interpretation |
| --- | --- | --- |
| Gyromite Test screen | A 10-second, 576-frame capture showed the chosen region almost continuously green. The revised Test detector recognized it and blinked the virtual head light. | Test acknowledgement works with this screen and crop. It does not establish movement decoding. |
| Gyromite Direct mode | RetroPie received button presses and showed Left/Right selections. Six spaced commands yielded no decoded robot actions. | Automatic optical movement is not yet ready for play. The controller rejected incomplete samples instead of moving incorrectly. |
| Gyromite frame trace | A command produced a brief green/white sequence several seconds after the input. The former mixed-brightness score treated white as green. Green dominance separates the two in the captured frames. | Correcting the color metric is necessary, but the current camera timing still misses or blends cells. |
| Stack-Up launch and modes | Both supplied archive formats were identified correctly by RetroPie and the UNO Q. On FCEUmm, Select opened the mode list and Start entered Test, Direct, and Memory. The ROBOT BLOCK artwork also appears during Test. | The apparent title-screen block was a menu-control misunderstanding, not a failed ROM launch. |
| Stack-Up Test signal | A direct 756-frame trace at 60.2 fps showed alternating white and green frames in the screen crop. The live UNO Q detector recognized the signal and blinked the red light; no movement event occurred. | Test acknowledgement works for Stack-Up with this crop. Movement command decoding remains unverified. |
| Recentered camera | The new sampling box landed on the full display. Stack-Up Test was detected again at 60 fps with the new region. Gyromite launched and was identified correctly; its Test mode was not repeated after repositioning. | The new framing is confirmed for Stack-Up Test. Gyromite Test had passed at the earlier camera position. |
| App restart | The saved sampling box stayed on the display when camera capture was started after a full App Lab container restart. Stack-Up launched and was identified, then exited cleanly. The Test signal did not register during this repeat, and its mode screen was not conclusively reached. | Camera setting persistence is verified; this repeat does not add another optical Test pass. |
| Stack-Up Direct controls | FCEUmm entered Direct mode with Player 1 Select and Start. Directional input was sent, but no complete optical movement command was established from that check. | The menu and player input path work; this does not certify automatic block movement. |
| Cleanup | The game was exited and the temporary RetroPie emulator override was removed. | RetroPie is back at its normal menu and default emulator configuration. |

The Test signal is a visual status check. Its red light must never move a virtual arm or game piece. The ROM-derived 13-frame command patterns remain the acceptance rule for motion. The attached camera's nominal 60 fps is very close to the NES frame rate; short cells can be skipped or mixed by camera phase, exposure, and display persistence. The synthetic timing tests do not prove reliable live decoding.

## RetroPie and registry check

- The live NES core is FCEUmm. Player 1 uses its regular joypad controls; the R.O.B. Vision virtual Controller 2 remains on Player 2. Nestopia was tried during diagnosis, then its temporary per-ROM override was removed.
- The registry on RetroPie, the UNO Q, and in this repository had the same SHA-256 hash. Live Gyromite and Stack-Up `.7z` launches selected the matching virtual game; exiting cleared the selection. Both archive formats were also launched during the optical investigation.
- The Sony pad had Select assigned both to the game and RetroArch's hotkey modifier. The hotkey is now L3 (button 11), game Select is button 9, and game Start is button 8. L3+R3 exits RetroArch and was tested with Stack-Up. The previous profile is backed up on RetroPie.

## Changes from this test

- Camera sampling now measures green dominance over both red and blue. This separates the captured green frames from white frames.
- Test acknowledgement accepts a green field held for at least 0.6 seconds, as well as regular alternating Test flashes. The browser calls this **Watch Test Signal**.
- The activity feed records one Test acknowledgement per arm instead of repeating it every camera frame.
- The App Lab entry point now loads a preferred sampling region from `data/camera-roi` (or `ROB_VISION_CAMERA_ROI`). Starting or reconnecting the camera reuses that region. The installed device stores the recentered region in its app data directory.

## Remaining validation

1. Capture confirmed Stack-Up Direct commands and compare each complete optical pattern with the ROM table. The Test signal is now confirmed and does not move virtual blocks.
2. Improve the command capture path and replay recorded live traces before permitting an action. Verify all commands in both games, with repeated trials and no false movement during idle or Test mode.
3. Check different screen positions, exposure settings, camera phase, and real gameplay timing. Keep the current fail-closed behavior until measured reliability is acceptable.
