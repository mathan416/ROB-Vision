# Optical game input: camera watching a modern display

## Current implementation

The UNO Q's optional OpenCV capture path watches the cabinet's LCD/OLED game display. It requests 60 fps, timestamps delivered frames, samples normalized green dominance from the central 60% rectangle by default, and passes samples to `controller/optical.py`. Setup shows a low-rate camera preview with the sampling rectangle, measured fps, and signal level. A CLI `--camera-roi x,y,width,height` can change the crop. The diagnostic camera trace also records a wide upper-frame average and 12 horizontal screen bands, but neither currently drives R.O.B. The browser does not offer a draggable crop or automatic display locator.

The decoder uses the ROM-derived `000101w1x1y1z` command family and a 60 Hz source-cell model. Six commands map to left, right, up, down, open, and close; Gyromite moves two levels vertically while Stack-Up moves one. Gyromite's sustained green field or Stack-Up's alternating green/white Test signal blinks R.O.B.'s red status light, and the ready-light command glows steadily without moving pieces. Only complete, unambiguous transmissions cause one model action. Partial or ambiguous samples are rejected. Separate repeated transmissions remain valid commands.

## Measured boundary

Synthetic stress tests with timing jitter at 60 fps decoded 667 of 900 valid command traces and rejected 233; none in that run became a wrong command. At 30 fps, all 900 were rejected. Ten further 900-trace seeds also produced zero wrong commands. These results show that conservative rejection works, but they do **not** establish reliable play. The attached Kiyo Pro delivered about 60 fps at 640×480, and both games' Test modes were recognized with a tight crop. A live Stack-Up RIGHT flash decoded and moved the virtual R.O.B. one station, but repeated commands were missed. A nominal 60 fps setting does not guarantee alignment with one-frame flashes. Frame drops, rolling shutter, display persistence, and video filters can change the signal.

After the camera was moved closer and aimed straight-on, the small dark crop and a wide average rose and fell on the same camera frames. The wide average did not recover the missing command cells. Twelve horizontal band measurements did reveal different green/dark levels at the top and bottom of individual frames, consistent with scan timing. One band decoded an UP signal in offline replay, but three further UP/RIGHT cycles yielded no complete decoder result from any band. UP_STACK (`0001011111010`) and RIGHT (`0001011101010`) differ only at bit 8, counting from zero; a missed green cell at that position can make UP resemble RIGHT. The band data is diagnostic only; no band can command R.O.B. until repeated tests establish correct identity and a low false-trigger rate.

## Commissioning test

1. Attach the intended camera, point it at the game's flash region, and use Setup's **Start Camera Check**. Check the delivered fps and green sample rectangle.
2. In each game's Test mode, choose **Watch Test Signal**. Confirm the Test signal blinks the virtual red light without causing movement. Repeat under normal room lighting and beside the UNO Q matrix.
3. Capture each of the six commands many times in both games, plus ready signals and idle gameplay. Compare accepted/rejected actions with what the game actually displayed. Include Stack-Up Memory speed and Bingo's no-command simultaneous row/column case.
4. Change display scaling, exposure, glare, and camera aim slightly. Record measured fps, dropped frames, decode counts, and false triggers. A proposed project target is at least 99 correct in 100 transmissions per command with zero idle false triggers; it has **not** been met.
5. If this camera path cannot meet the target at the available 30–60 fps, consider an authenticated emulator command hook. That hook is not implemented.

Nintendo's [photosensing patent](https://patents.google.com/patent/US4815733A/en) and the [historical manual](HISTORICAL_MANUAL_NOTES.md) explain the original CRT light mechanism. They do not prove a modern camera/display combination will work. The [ROM analysis](ROM_SIGNAL_ANALYSIS.md) gives the exact patterns; the [synthetic test report](UNATTENDED_TEST_REPORT_2026-09-24.md) and [live optical test report](LIVE_OPTICAL_TEST_2026-09-25.md) separate simulation from hardware results.
