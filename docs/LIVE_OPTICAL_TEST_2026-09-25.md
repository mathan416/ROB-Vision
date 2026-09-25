# Live optical test - 25 September 2026

**Later result, same day:** The camera findings below remain valid for camera-only play. A separate RetroPie frame link was subsequently installed and decoded all six command types in both games during live Direct play. See the [frame-link report](FRAME_LINK_TEST_2026-09-25.md). Statements below that the emulator hook is unimplemented describe the earlier test stage.

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
- The user remapped the Sony pad in EmulationStation. The resulting profile has Select on button 8, Start on button 9, and the hotkey on button 10. Independent test inputs also worked through RetroArch's configured keyboard directions. The user's generated pad profile was left intact.

## Changes from this test

- Camera sampling now measures green dominance over both red and blue. This separates the captured green frames from white frames.
- Test acknowledgement accepts a green field held for at least 0.6 seconds, as well as regular alternating Test flashes. The browser calls this **Watch Test Signal**.
- The activity feed records one Test acknowledgement per arm instead of repeating it every camera frame.
- The App Lab entry point now loads a preferred sampling region from `data/camera-roi` (or `ROB_VISION_CAMERA_ROI`). Starting or reconnecting the camera reuses that region. The installed device stores the recentered region in its app data directory.

## Remaining validation

1. Capture confirmed Stack-Up Direct commands and compare each complete optical pattern with the ROM table. The Test signal is now confirmed and does not move virtual blocks.
2. Improve the command capture path and replay recorded live traces before permitting an action. Verify all commands in both games, with repeated trials and no false movement during idle or Test mode.
3. Check different screen positions, exposure settings, camera phase, and real gameplay timing. Keep the current fail-closed behavior until measured reliability is acceptable.

## Independent Stack-Up Direct-mode follow-up

- RetroPie was navigated into Stack-Up Direct mode and Hector was moved onto the actual RIGHT arrow using configured inputs. A short RetroArch recording showed the exact 13 rendered frames `0001011101010`, the ROM-derived RIGHT pattern. The temporary recording configuration was removed afterward; the original NES configuration was restored exactly.
- A camera trace with a long dark idle before the flash contained all 13 cells. The decoder had rejected it because it counted the entire idle stretch as the three-frame preamble. It now trims that stretch and tests the phase of the first bright sample. A second live trace had a 9 ms dark cell; accepting a half-frame timing error while still requiring a unique sampled pattern recovered RIGHT in replay. All 42 local tests pass, including these two trace shapes and idle false-trigger checks.
- The Kiyo Pro was tested with HDR off, 640×480 MJPEG near 60 delivered fps, and manual exposure 10 (1 ms). Automatic exposure blended the dark cells. The controller now applies that measured setting when it starts or reconnects this camera. The saved crop on this UNO Q is `0.32,0.15,0.045,0.05`; this is specific to the current physical aim.
- In one live, independently triggered UP then RIGHT sequence, both commands decoded. UP was blocked because the arms were already at the top; RIGHT moved the virtual R.O.B. from station 3 to 4. After a later controller restart, another RIGHT trace was uniquely recoverable in offline replay but was just outside the earlier timing threshold. A final live sequence after deploying that adjustment was fully green in the camera samples, so no command decoded and R.O.B. correctly remained still.
- Four additional hands-free UP/RIGHT cycles on the final deployment generated 80 bright camera samples but zero decoded commands. The virtual station stayed at 3. This confirms that the single successful live sequence does not represent dependable capture with the present 60 fps camera and LCD timing.
- **Result:** automatic Stack-Up movement has been demonstrated end to end, but the 60 fps camera and display are not reliable enough for unattended play. The emulator's rendered 13-frame pattern is correct; the remaining loss is in optical capture. Gyromite automatic movement has not yet been demonstrated live. Keep the strict decoder; do not infer a command from an all-green or incomplete burst.
- The measured next route for dependable RetroPie play is a frame-level emulator output hook that forwards only a fully matched 13-frame optical command to the UNO Q. This has not been implemented or validated. The camera path can remain available for original hardware and Test-mode checks.

## Closer, straight-on camera and dual-region check

- The user moved the camera closer and aimed it directly at the display. The saved dark sampling box moved to `0.205,0.15,0.04,0.05`; the game is centered and fills more of the 640×480 image. Delivered capture remained about 60 fps.
- The controller now records three diagnostic traces per frame: the dark box, a wide upper-frame average, and 12 horizontal bands across the game display. Only the dark-box trace drives the existing strict decoder.
- An independent Stack-Up Direct-mode UP/RIGHT sequence produced visible pulses in both small and wide averages, but neither decoded a complete command. The wide average tracked the same missing cells as the small box. A horizontal band recovered UP once in offline replay, showing that row timing contains extra information. Three more independent UP/RIGHT cycles yielded no complete command from any band, and R.O.B. stayed at station 3.
- UP_STACK and RIGHT differ at only one of their 13 bits. Losing the green UP cell at that position can make a trace resemble RIGHT. A permissive decoder could therefore move R.O.B. the wrong way. The band trace remains diagnostic until command identity and false-trigger rates are validated over repeated trials.

## Direct-mode comparison across movement directions

The same RetroPie session was driven independently across the Stack-Up Direct grid while RetroArch recorded its rendered frames and the UNO Q logged camera samples. The emulator rendered full, exact 13-frame messages for UP_STACK (`0001011111010`), LEFT (`0001010111010`), DOWN_STACK (`0001010101110`), and RIGHT (`0001011101010`). It also rendered OPEN during a move onto that square. These are game output, not inferred camera commands.

| Source command | Camera observation | Live controller result |
| --- | --- | --- |
| UP_STACK, first transmission | The dark-box and wide traces preserved the active sequence and the green ninth bit, but frame timing did not satisfy the strict decoder. | Rejected. |
| LEFT | The dark-box and wide traces preserved a different active sequence and the green ninth bit; timing still prevented a complete decode. | Rejected. |
| UP_STACK, later transmission | Several camera cells blended together, including a long green run. | Rejected. |
| DOWN_STACK | The active sequence, including its dark ninth bit, was distinguishable. | **Decoded live; virtual arm height moved from 6 to 5.** |
| RIGHT | The camera sequence had extra or blended cells and could not be aligned uniquely with the rendered pattern. | Rejected. |

The ninth bit is not consistently absent. Different transmissions lose or blend different cells, and some preserve the distinguishing bit while still failing timing validation. The wide upper-frame average followed the dark-box trace closely; it did not fill the missing samples. Keep movement decoding strict until a method can identify every command without mistaking one direction for another.

## Kiyo Pro capture-mode investigation

- The attached Kiyo Pro is on a 5 Gbit/s USB 3 link. It enumerates MJPEG, YUYV, NV12, and H264 capture formats through 1920×1080 at 60 fps; `/dev/video3` is a separate UVC metadata node with `UVCH` format.
- A device-local capture-mode switch allowed comparison of the normal 640×480 MJPEG pipeline with 1280×720 uncompressed YUYV. After moving the normalized sampling box to the actual dark display patch, YUYV delivered about 60 fps. In a source-recorded UP, LEFT, UP run, the camera decoded LEFT but missed both UP commands. The capture mode alone did not solve reliability.
- The minimum exposed shutter setting, 0.3 ms, produced an overexposed image and about 30 delivered fps during this trial. The 1 ms setting was restored.
- Standalone raw NV12 1920×1080 capture with OpenCV color conversion disabled delivered 660 frames in 11.9 seconds, around 60 fps. Full BGR conversion delivered only about 36 fps in the same benchmark. A first raw-row trace sampled outside the active flash area and is inconclusive; no row-timing decoder has been deployed.
- The app was restored to 640×480 MJPEG, the saved `0.205,0.15,0.04,0.05` region, and 1 ms exposure. Its camera state was verified as capturing at 60.1 fps, with Stack-Up and RetroPie still linked.

## Raw 1080p and Kiyo zoom follow-up

The UNO Q captured two further 1,800-frame raw NV12 sessions at about 60 fps, each aligned with independently triggered Stack-Up Direct moves and RetroArch source recordings. Three narrow vertical strips, with 24 row bands each, measured luma and V chroma. Normal framing recovered two of four source-recorded commands exactly in the frame average; none of the 72 bands recovered the two rejected commands. The Kiyo Pro's zoom and tilt controls then enlarged the game display from roughly half the frame height to most of it. In that framing, only one of four source-recorded commands matched exactly, and no band recovered the other three. [The row-test report](KIYO_PRO_ROW_TEST_2026-09-25.md) records each command and the safety implication. No row-based action path was deployed.

The separate UVC metadata node yielded 30 nonempty timing records while the normal preview ran, confirming that camera and USB timing can be measured more precisely in a future capture path. Camera zoom, tilt, exposure, capture mode, and crop were restored after testing; the live preview returned to about 60 fps with RetroPie online.
