# R.O.B. Vision

R.O.B. Vision plays Gyromite and Stack-Up with a **virtual robot companion**. The Arduino UNO Q owns the companion's pose and game pieces. RetroPie or Batocera sends game light commands from rendered NES frames to the UNO Q over Wi-Fi or Ethernet. A browser on a laptop, iPad, or phone animates the robot, gyros, spinner, pads, trays, and blocks. Gyromite's virtual Controller 2 buttons return to the game console over the network.

**Meet Buddy:** a little robot follows the game's light signals beyond the emulator. His first blink appears on the UNO Q; his movements appear in the browser. Read [Buddy's story](docs/MEET_BUDDY.md).

The Buddy-led public website for `rob-vision.mathan.ca` is in [website](website/). It is a static site prepared for manual upload to the domain's web root.

The app includes Mission and Setup pages, paired RetroPie and Batocera links, FCEUmm and Nestopia frame wrappers, Gyromite gate controls, Stack-Up blocks, UNO Q matrix animations, and demos that run while no game is active.

Start **R.O.B. Vision** from UNO Q App Lab **My Apps**, then open `http://<your-uno-q-hostname>.local/dashboard/` or `http://<your-uno-q-LAN-IP>/dashboard/` on a laptop, phone, or tablet. The installer prints the actual Mission and Setup URLs for your UNO Q. Stop another App Lab app before starting R.O.B. Vision. Browser controls work on your trusted local network; keep the app off the public Internet.

The [Setup page](dashboard/setup.html) pairs either console, shows receiver and game-frame status, acknowledges Test mode from the frame link, and offers Gyromite and Stack-Up manual checks. [Mission](dashboard/index.html) keeps R.O.B. and the Game Table as the main view. The [Help center](dashboard/help.html) covers play, controls, indicators, and troubleshooting.

## Install version 0.1.6

The public release provides one command for the UNO Q and the same console command for RetroPie or Batocera. Run the UNO Q command as `arduino`:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/download/v0.1.6/install.sh | sh -s -- uno-q
```

Run the console command on RetroPie as `pi`, or on Batocera as `root`, replacing the UNO Q hostname:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/download/v0.1.6/install.sh | sh -s -- console your-uno-q.local
```

The console command installs the receiver, starts a first-time pairing window, and prints a code and fingerprint. Enter them on the UNO Q [Setup page](dashboard/setup.html). Pairing starts the receiver and configures Gyromite's virtual Controller 2; no further console command is needed. Upgrades preserve existing pairing. See the [installation guide](docs/INSTALLATION_GUIDE.md) for requirements, supported Batocera hardware, repair, and verification.

## Play through Batocera

Batocera 43.1 x86_64 is supported alongside RetroPie. The installer selects the R.O.B. Vision FCEUmm wrapper for the exact Gyromite and Stack-Up ROM names, with Nestopia available as a per-game choice. It adds a separate Batocera service and launch hook. Install and pair using the [Batocera guide](deploy/batocera/README.md).

Setup's **Console Link** lists paired consoles individually, including online status. Use **Pair Another Console** to add one and **Remove** to revoke one console's credential without disconnecting the others. Only one console supplies the active game at a time.

## Play through RetroPie

Install the [RetroPie receiver and launch choices](deploy/retropie/README.md), then pair the console on Setup. For a supported game, select `lr-robvision-fceumm` or `lr-robvision-nestopia` in RetroPie's emulator selection. These entries use the installed original cores through a small frame wrapper; they are not separate emulators. The plain `lr-fceumm` and `lr-nestopia` entries play the game without R.O.B. Vision's automatic movement link.

A registered ROM launch selects Gyromite or Stack-Up on the UNO Q. **GAME FRAMES LINKED** confirms that the selected game is sending frames. A complete 13-frame command changes the virtual model; Test-mode flashes blink R.O.B.'s red status light without moving him. In Gyromite, a gyro on a pad or an immediate **Fast Gates** hold sends red or blue to the active console's virtual Controller 2. Fast Gates use **2** for blue, **1** for red, and **0** to release both; each hold expires after 60 seconds.

When no supported game is active, **Run Demo Sequence** shows the Gyromite relay or Stack-Up transfers, even if a console is paired. **Home** resets the selected virtual game. The local `file://` dashboard is an offline preview; it does not show live UNO Q or console state.

For local development, run `python3 -m controller.service` and open `http://127.0.0.1:8766/dashboard/`. For trusted-LAN access use `ROB_VISION_TOKEN` and `--host 0.0.0.0`. The game host can identify launches with [`tools/notify_game.py`](tools/notify_game.py), using the exact names in [`config/games.json`](config/games.json). User-supplied ROMs and tokens stay outside this repository.

## Guides

Start with [Installation & Setup](docs/INSTALLATION_AND_SETUP.md), the [Game Manual](docs/GAME_MANUAL.md), and the [User Guide](docs/USER_GUIDE.md). The [Buddy Story Comic](docs/BUDDY_COMIC.md), [Technical Reference](docs/TECHNICAL_ARCHITECTURE.md), [Technical Test Results](docs/TEST_RESULTS_TECHNICAL.md), [Engineering Journey](docs/ENGINEERING_JOURNEY.md), and [release notes](docs/RELEASE_NOTES_0.1.6.md) provide more detail. Printable editions are under [output/pdf](output/pdf).

Historical Nintendo manuals and the Robert project informed behavior, but their text or code is not reused here. Nintendo's characters, game artwork, and marks remain with their owners. R.O.B. Vision is not affiliated with or endorsed by Nintendo.
