# Live optical test - 25 September 2026

## Setup

- R.O.B. Vision ran on the Arduino UNO Q at `arduiain.local`; RetroPie ran at `retropie.local` and sent authenticated game launch and exit events.
- A Razer Kiyo Pro connected to the UNO Q watched the modern display. It delivered approximately 59.8-60 frames per second at 640 x 480 MJPEG with HDR temporarily disabled.
- The Gyromite Test screen was framed with a tight normalized camera region of `0.4,0.54,0.055,0.06`. The region and camera placement are specific to this test.
- The games were the user's supplied world ROM archives. No ROM is included in this repository.

## What happened

| Check | Live result | Interpretation |
| --- | --- | --- |
| Gyromite Test screen | A 10-second, 576-frame capture showed the chosen region almost continuously green. The revised Test detector recognized it and blinked the virtual head light. | Test acknowledgement works with this screen and crop. It does not establish movement decoding. |
| Gyromite Direct mode | RetroPie received button presses and showed Left/Right selections. Six spaced commands yielded no decoded robot actions. | Automatic optical movement is not yet ready for play. The controller rejected incomplete samples instead of moving incorrectly. |
| Gyromite frame trace | A command produced a brief green/white sequence several seconds after the input. The former mixed-brightness score treated white as green. Green dominance separates the two in the captured frames. | Correcting the color metric is necessary, but the current camera timing still misses or blends cells. |
| Stack-Up launch | Both supplied archive formats were identified correctly by RetroPie and the UNO Q. The game stayed on the Robot Block title screen under the tested FCEUmm and Nestopia configurations. | Stack-Up Test and movement screens were not reached; its optical path remains unverified. |
| Cleanup | The game was exited and the temporary RetroPie emulator override was removed. | RetroPie is back at its normal menu and default emulator configuration. |

The Test signal is a visual status check. Its red light must never move a virtual arm or game piece. The ROM-derived 13-frame command patterns remain the acceptance rule for motion. The attached camera's nominal 60 fps is very close to the NES frame rate; short cells can be skipped or mixed by camera phase, exposure, and display persistence. The synthetic timing tests do not prove reliable live decoding.

## Changes from this test

- Camera sampling now measures green dominance over both red and blue. This separates the captured green frames from white frames.
- Test acknowledgement accepts a green field held for at least 0.6 seconds, as well as regular alternating Test flashes. The browser calls this **Watch Test Signal**.
- The activity feed records one Test acknowledgement per arm instead of repeating it every camera frame.

## Remaining validation

1. Reach Stack-Up's Test screen and confirm its optical signal without moving virtual blocks.
2. Improve the command capture path and replay recorded live traces before permitting an action. Verify all commands in both games, with repeated trials and no false movement during idle or Test mode.
3. Check different screen positions, exposure settings, camera phase, and real gameplay timing. Keep the current fail-closed behavior until measured reliability is acceptable.
