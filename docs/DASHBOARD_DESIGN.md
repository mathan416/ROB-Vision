# Laptop, tablet, and phone dashboard

The running Mission page puts virtual R.O.B. and the accessories first. A browser served by the UNO Q follows its controller snapshot; the same files opened directly through `file://` run the independent scripted preview. Camera framing belongs on Setup, not in the main view.

## Mission layout

The large Live Model animates R.O.B.'s connected shoulders, shared opposing hands, head turn, and vertical carriage. Accessory Bay and Game Table show the same gyro or block state. Gyromite has two holders, a spinner, red/blue pads, and two gyros; Stack-Up has five trays and all five blocks. Pose Preview, Game Table, and System Vitals are grouped beneath the model. The Activity Feed distinguishes manual, optical, and link events. The selected game and RetroPie connection are separate statuses: `GYROMITE / CONNECTED` means Gyromite is selected and the browser reaches the UNO Q. The separate **RETROPIE ONLINE/OFFLINE** indicator reports receiver polling.

Fast Gates appears during live Gyromite when camera capture is stopped. Blue (`2`), red (`1`), and Release Both (`0`) act immediately; each hold expires after 60 seconds. A manual pose preview or scripted demo is not evidence of a decoded game command. Demo mode can run while RetroPie is paired and idle; a game launch stops it.

## Setup layout

Setup contains RetroPie pairing and **Check Link**, camera framing and measured fps, Test-mode flash watching and red-light preview, Gyromite pad checks, and Stack-Up movement checks. The small camera image marks the sampled region. **Reset & Reconnect** reopens OpenCV capture after a disconnect; it does not reset USB hardware. Camera diagnostics remain available even though the main visual focus is R.O.B.

## State and limits

`dashboard/live.js` polls `/api/state` every 500 ms and enters live mode when the controller responds. The UNO Q owns game, pose, pieces, and pad state; a browser reload simply resumes from the latest snapshot. The last 30 controller events are display history, not a guaranteed command log. Camera frames are low-rate JPEG previews for alignment, while decoding consumes timestamped frames in the controller. The browser cannot verify Hector's location, Stack-Up scoring, or a visible gate response.

The static preview demonstrates a finite Gyromite spin/return sequence, Stack-Up block transfers, and Pose Lab. Its graphics are original SVG/CSS art informed by the [historical manual notes](HISTORICAL_MANUAL_NOTES.md). Camera-driven animation still awaits real display/camera testing.
