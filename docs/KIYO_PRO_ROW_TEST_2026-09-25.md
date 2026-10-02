# Kiyo Pro raw-row optical test — 25 September 2026

> Archived camera research. R.O.B. Vision now receives game commands and Test signals only through RetroPie rendered frames.

## Question

Could uncompressed 1080p camera frames reveal enough subframe scan timing to recover Stack-Up commands that the 60 fps whole-frame decoder misses?

## Setup and method

- The actual Kiyo Pro on the UNO Q was connected at USB 3 SuperSpeed. HDR was off; manual exposure was 1 ms. RetroPie ran Stack-Up Direct mode with FCEUmm on the intended LCD.
- A temporary root uinput **keyboard** on RetroPie pressed the mapped Player 1 arrow keys. This moved Hector on the visible board without altering the user's controller mapping. RetroArch simultaneously recorded its rendered game output. The camera diagnostic had no path to move virtual R.O.B.
- The UNO Q captured raw NV12 at 1920×1080, with OpenCV colour conversion disabled. It sampled three 55-pixel-wide strips, 24 horizontal bands in each, recording luma and the NV12 V chroma component. A chroma value below 0.35 was classified as green for this offline comparison.
- The first aligned run used the normal camera framing and bands across the upper 510 image rows. A second run used the camera's volatile zoom (`180`) and upward digital tilt (`36000`) to make the game image occupy about 900 of 1080 rows. The diagnostic then sampled bands across those 900 rows.
- The RetroArch source patterns are compared with only the four commands fully present in each source recording. The fifth key press in each run happened near recording shutdown and is excluded from the source-aligned score.

## Results

Both camera runs delivered 1,800 frames at approximately 60 fps. The source recording contained complete 13-frame command patterns for the first four moves in each run.

| Framing | Source command | Camera average | Exact row regions |
| --- | --- | --- | ---: |
| Normal | UP_STACK `0001011111010` | Exact | 69/72 |
| Normal | LEFT `0001010111010` | Exact | 69/72 |
| Normal | UP_STACK `0001011111010` | `0001011111011` | 0/72 |
| Normal | RIGHT `0001011101010` | Best alignment differed by two bits | 0/72 |
| Zoom and tilt | RIGHT `0001011101010` | Exact | 69/72 |
| Zoom and tilt | UP_STACK `0001011111010` | Best alignment differed by two bits | 0/72 |
| Zoom and tilt | LEFT `0001010111010` | Best alignment differed by three bits | 0/72 |
| Zoom and tilt | UP_STACK `0001011111010` | Best alignment differed by two bits | 0/72 |

The third normal-view camera pattern is a valid bit pattern for **Gyromite** DOWN, but it is not a valid Stack-Up command. The controller's game-specific action set would reject it. This illustrates why guessing or accepting a closest pattern could cause a wrong movement.

The 72 bands cover three strips × 24 vertical regions. For each region, the offline check tried a start shift of up to three captured frames and asked whether its 13 binary samples matched the source command exactly. The rejected commands did not become exact in any band. The results therefore do **not** support routing row measurements into the live movement decoder. Green frames had a consistent top-to-bottom intensity gradient, but that gradient was also present across repeated green frames and did not reveal the missing command cells.

## Kiyo Pro timing metadata

The separate `/dev/video3` UVC metadata node streamed concurrently with the restored preview. Thirty blocks yielded 660 bytes: 22 bytes per block, comprising an eight-byte host timestamp, two-byte USB start-of-frame number, and a 12-byte UVC payload header. The header flags indicated PTS and SCR fields. Host inter-block intervals had a median of 16.63 ms, with a 14.22–21.37 ms range in this short run. This is useful for measuring capture timing more accurately than the current `time.monotonic()` call after `capture.read()`. It cannot supply pixel values for a missed display cell.

## Engineering conclusion

Uncompressed NV12 and direct chroma sampling let the UNO Q process full-resolution Kiyo Pro frames near 60 fps. Digital zoom and tilt improve framing but did not improve command recovery in the tested LCD setup. Sampling rows separately did not recover any rejected source-aligned command. The existing strict decoder and non-motion diagnostic bands remain the appropriate live behaviour.

The remaining timing limit is the free-running 60 fps camera observing roughly 60 Hz one-frame game cells through the display pipeline. A future experiment should first establish whether a different physical camera position or display mode produces genuine within-frame transitions; this result gives no evidence for changing the live decoder. For dependable RetroPie play, a frame-level emulator output hook remains the measured fallback; the camera can still be used for camera placement, Test-mode light, and original-hardware trials.

After the experiment, the Kiyo Pro was returned to zoom `100`, pan `0`, tilt `0`, and 1 ms exposure. The app was returned to 640×480 MJPEG with its original saved sampling box. The live status again showed Stack-Up selected, the camera capturing near 60 fps, and RetroPie online.

Related: [optical input](optical-input.md), [ROM signal analysis](ROM_SIGNAL_ANALYSIS.md), and [earlier live optical tests](LIVE_OPTICAL_TEST_2026-09-25.md).
