# Laptop, tablet, and phone dashboard

The running Mission page puts virtual R.O.B. and the accessories first. A browser served by the UNO Q follows its controller snapshot; the same files opened directly through `file://` run the independent scripted preview. Setup shows frame-link and Test status.

## Mission layout

The large Live Model animates R.O.B.'s connected shoulders, shared opposing hands, head turn, and vertical carriage. Accessory Bay and Game Table show the same gyro or block state. Gyromite has two holders, a spinner, red/blue pads, and two gyros; Stack-Up has five trays and all five blocks. Pose Preview, Game Table, and System Vitals are grouped beneath the model. The Activity Feed distinguishes manual, game-frame, and link events. The top status uses **GYROMITE / CONNECTED**, **STACK-UP / CONNECTED**, or **NO GAME / CONNECTED** to show browser reachability and the selected game. A separate **RETROPIE / LINKED**, **BATOCERA / LINKED**, or **RECALBOX / LINKED** status reports a recent receiver check-in; **WAITING** means no recent check-in. **GAME FRAMES IDLE**, **WAITING**, and **LINKED** distinguish no selected game, missing frames, and an active frame link.

Fast Gates appears during live Gyromite. Blue (`2`), red (`1`), and Release Both (`0`) act immediately; each hold expires after 60 seconds. A manual pose preview or scripted demo is not evidence of a decoded game command. Demo mode can run while a console is paired and idle; a game launch stops it.

![Live Mission page with R.O.B. and Gyromite accessories](images/mission-model-screenshot.png)

![Mission control row with Pose Preview, Game Table, and System Vitals](images/mission-controls-screenshot.png)

![Stack-Up Game Table illustration with five trays and the starting block stack](images/stack-up-game-table.png)

## Setup layout

Setup lists paired RetroPie, Batocera, and Recalbox consoles and provides **Check Link**, frame-link status, Test-mode indication and red-light preview, Gyromite pad checks, and Stack-Up movement checks.



## State and limits

`dashboard/live.js` polls `/api/state` every 500 ms and enters live mode when the controller responds. The UNO Q owns game, pose, pieces, and pad state; a browser reload simply resumes from the latest snapshot. The last 30 controller events are display history, not a guaranteed command log. The browser cannot verify Hector's location, Stack-Up scoring, or a visible gate response.

The static preview demonstrates a finite Gyromite spin/return sequence, Stack-Up block transfers, and Pose Lab. Its graphics are original SVG/CSS art informed by the [historical manual notes](HISTORICAL_MANUAL_NOTES.md). Frame-driven animation was observed in both supported games.
