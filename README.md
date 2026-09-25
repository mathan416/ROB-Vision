# R.O.B. Vision

R.O.B. Vision brings Nintendo's Robotic Operating Buddy to life as a **virtual robot**. The Arduino UNO Q owns R.O.B.'s pose and game pieces. RetroPie sends Gyromite and Stack-Up light commands from each rendered NES frame to the UNO Q over Wi-Fi or Ethernet. A browser on a laptop, iPad, or phone animates the robot, gyros, spinner, pads, trays, and blocks. Gyromite's virtual Controller 2 buttons return to RetroPie over the network. There is no physical robot or camera.

**Available now:** a separate UNO Q App Lab app, live Mission and Setup pages, exact ROM identification, paired RetroPie receiver, FCEUmm and Nestopia game-frame launch choices, Gyromite gate return, Stack-Up block model, UNO Q matrix animations, and offline demonstrations. Live Direct play delivered all six command types from both games through FCEUmm; Nestopia delivered movement commands from both games. Both Gyromite gate colors were confirmed in Game A under FCEUmm. Nestopia gate return and longer game sessions remain to be checked.

Start **R.O.B. Vision** from UNO Q App Lab **My Apps**, then open `http://arduiain.local/dashboard/`. The direct `http://arduiain.local:8766/dashboard/` address uses the same controller state. This UNO Q runs one App Lab app at a time, so stop VirtualGlove before starting R.O.B. Vision. The browser controls are available on the trusted LAN without a token prompt. The token stored in the UNO Q's `~/.config/rob-vision/environment` is used for authenticated RetroPie launch and receiver traffic. Do not expose the service to the public Internet.

The [Setup page](dashboard/setup.html) pairs RetroPie, shows receiver and game-frame status, acknowledges Test mode from the frame link, and offers Gyromite and Stack-Up manual checks. [Mission](dashboard/index.html) keeps R.O.B. and the Game Table as the main view. The [Help center](dashboard/help.html) covers play, controls, indicators, and troubleshooting.

## Play through RetroPie

Install the [RetroPie receiver and launch choices](deploy/retropie/README.md), then pair the console on Setup. For a supported game, select `lr-robvision-fceumm` or `lr-robvision-nestopia` in RetroPie's emulator selection. These entries use the installed original cores through a small frame wrapper; they are not separate emulators. The plain `lr-fceumm` and `lr-nestopia` entries play the game without R.O.B. Vision's automatic movement link.

A registered ROM launch selects Gyromite or Stack-Up on the UNO Q. **GAME FRAMES LINKED** confirms that the selected game is sending frames. A complete 13-frame command changes the virtual model; Test-mode flashes blink R.O.B.'s red status light without moving him. In Gyromite, a gyro on a pad or an immediate **Fast Gates** hold sends red or blue to RetroPie's virtual Controller 2. Fast Gates use **2** for blue, **1** for red, and **0** to release both; each hold expires after 60 seconds.

When RetroPie is idle, **Run Demo Sequence** shows the Gyromite relay or Stack-Up transfers. **Home** resets the selected virtual game. The local `file://` dashboard is an offline preview; it does not show live UNO Q or RetroPie state.

For local development, run `python3 -m controller.service` and open `http://127.0.0.1:8766/dashboard/`. For trusted-LAN access use `ROB_VISION_TOKEN` and `--host 0.0.0.0`. The game host can identify launches with [`tools/notify_game.py`](tools/notify_game.py), using the exact names in [`config/games.json`](config/games.json). User-supplied ROMs and tokens stay outside this repository.

## Guides and release status

Start with the [documentation index](docs/INDEX.md), [user guide](docs/USER_GUIDE.md), [setup guide](docs/SETUP_GUIDE.md), [technical architecture](docs/TECHNICAL_ARCHITECTURE.md), and [release review](docs/RELEASE_REVIEW_2026-09-25.md). Printable editions are under [output/pdf](output/pdf). The remaining live checks include longer sessions, Stack-Up Memory/Bingo, Nestopia Game A gate return, and simultaneous browser clients.

Historical Nintendo manuals and the Robert project informed behavior, but their text or code is not reused here. Game artwork and Nintendo marks remain with their owners.
