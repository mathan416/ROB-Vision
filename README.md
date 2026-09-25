# R.O.B. Vision

R.O.B. Vision is an independent maker project for playing Gyromite and Stack-Up with a **virtual robot companion**. The Arduino UNO Q owns the companion's pose and game pieces. RetroPie or Batocera sends game light commands from each rendered NES frame to the UNO Q over Wi-Fi or Ethernet. A browser on a laptop, iPad, or phone animates the robot, gyros, spinner, pads, trays, and blocks. Gyromite's virtual Controller 2 buttons return to the game console over the network. There is no physical robot or camera.

**Meet Buddy:** our working character concept is a little robot finding his way out of an emulator through the game-frame link. His first blink appears on the UNO Q; his movements appear in the browser. The [story brief](docs/BUDDY_STORY.md) develops that premise and sets boundaries for an original character. Buddy is a working nickname, not a cleared public brand.

**Available now:** a separate UNO Q App Lab app, live Mission and Setup pages, exact ROM identification, paired RetroPie and Batocera receivers, FCEUmm and Nestopia game-frame choices, Gyromite gate return, Stack-Up block model, UNO Q matrix animations, and offline demonstrations. Live Direct play delivered all six command types from both games through FCEUmm; Nestopia delivered movement commands from both games. Both Gyromite gate colors were confirmed in Game A under FCEUmm. Nestopia gate return and longer game sessions remain to be checked.

Start **R.O.B. Vision** from UNO Q App Lab **My Apps**, then open `http://arduiain.local/dashboard/` on the test device or your UNO Q's own hostname. The direct port 8766 address uses the same controller state. This UNO Q runs one App Lab app at a time, so stop VirtualGlove before starting R.O.B. Vision. The browser controls are available on the trusted LAN without a token prompt. The installer creates a private token in the UNO Q app's `data/controller-token`; an existing `ROB_VISION_TOKEN` environment setting takes precedence. That token authenticates RetroPie launch and receiver traffic. Do not expose the service to the public Internet.

The [Setup page](dashboard/setup.html) pairs either console, shows receiver and game-frame status, acknowledges Test mode from the frame link, and offers Gyromite and Stack-Up manual checks. [Mission](dashboard/index.html) keeps R.O.B. and the Game Table as the main view. The [Help center](dashboard/help.html) covers play, controls, indicators, and troubleshooting.

## Install (development preview)

The installers support an Arduino UNO Q running App Lab, standard RetroPie with the `pi` account, and Batocera 43.1 x86_64. They do not include ROMs or stock emulator cores. The UNO Q needs Python 3.9 or newer; RetroPie needs Python 3.7 or newer, `gcc`, `openssl`, and either `lr-fceumm` or `lr-nestopia`. Batocera needs FCEUmm or Nestopia and uses bundled x86_64 frame wrappers. The UNO Q installer stops and restarts R.O.B. Vision automatically. Exit any game on the target console before installing or upgrading.

The GitHub repository is currently private, so cloning requires an account with access and working GitHub authentication on each device. To keep GitHub credentials off the devices, transfer a clean archive from an authorized computer as shown in the [installation guide](docs/INSTALLATION_GUIDE.md). With GitHub access configured, clone this `dev` branch separately on each device. On the **UNO Q**, sign in as `arduino` and run:

```sh
git clone --branch dev https://github.com/mathan416/ROB-Vision.git ~/rob-vision-src
python3 ~/rob-vision-src/scripts/install.py uno-q
```

The installer starts **R.O.B. Vision** in App Lab. Open `http://<your-uno-q-name>.local/dashboard/setup.html`. On **RetroPie**, sign in as `pi` and run (replace the controller name):

```sh
git clone --branch dev https://github.com/mathan416/ROB-Vision.git ~/rob-vision-src
sudo python3 ~/rob-vision-src/scripts/install.py retropie --controller your-uno-q.local
python3 /home/pi/rob-vision/tools/retropie_pair.py
```

Enter the displayed code and certificate fingerprint on the UNO Q Setup page. Then on RetroPie run `sudo systemctl enable --now rob-vision-controller2.service` and `sudo python3 ~/rob-vision-src/scripts/install.py player2` to map the detected virtual pad. Restart the game after mapping. See the [installation guide](docs/INSTALLATION_GUIDE.md) for upgrades, checks, and supported layouts. Both the UNO Q and RetroPie installers passed in-place upgrades and repeat installs on the test devices, with pairing and the live link preserved. A fresh two-device installation has not yet been exercised.

## Play through Batocera

Batocera 43.1 x86_64 is supported alongside RetroPie. The installer selects the R.O.B. Vision FCEUmm wrapper for the exact Gyromite and Stack-Up ROM names, with Nestopia available as a per-game choice. It adds a separate Batocera service and launch hook; VirtualGlove's installation and Super Glove Ball choice remain intact. Install and pair using the [Batocera guide](deploy/batocera/README.md). Live launch, frame-link, and Gyromite Controller 2 configuration checks passed on the test Batocera machine; a full Batocera playthrough remains to be checked.

## Play through RetroPie

Install the [RetroPie receiver and launch choices](deploy/retropie/README.md), then pair the console on Setup. For a supported game, select `lr-robvision-fceumm` or `lr-robvision-nestopia` in RetroPie's emulator selection. These entries use the installed original cores through a small frame wrapper; they are not separate emulators. The plain `lr-fceumm` and `lr-nestopia` entries play the game without R.O.B. Vision's automatic movement link.

A registered ROM launch selects Gyromite or Stack-Up on the UNO Q. **GAME FRAMES LINKED** confirms that the selected game is sending frames. A complete 13-frame command changes the virtual model; Test-mode flashes blink R.O.B.'s red status light without moving him. In Gyromite, a gyro on a pad or an immediate **Fast Gates** hold sends red or blue to RetroPie's virtual Controller 2. Fast Gates use **2** for blue, **1** for red, and **0** to release both; each hold expires after 60 seconds.

When RetroPie is idle, **Run Demo Sequence** shows the Gyromite relay or Stack-Up transfers. **Home** resets the selected virtual game. The local `file://` dashboard is an offline preview; it does not show live UNO Q or RetroPie state.

For local development, run `python3 -m controller.service` and open `http://127.0.0.1:8766/dashboard/`. For trusted-LAN access use `ROB_VISION_TOKEN` and `--host 0.0.0.0`. The game host can identify launches with [`tools/notify_game.py`](tools/notify_game.py), using the exact names in [`config/games.json`](config/games.json). User-supplied ROMs and tokens stay outside this repository.

## Guides and release status

Start with the [documentation index](docs/INDEX.md), [user guide](docs/USER_GUIDE.md), [setup guide](docs/SETUP_GUIDE.md), [technical architecture](docs/TECHNICAL_ARCHITECTURE.md), and [release review](docs/RELEASE_REVIEW_2026-09-25.md). Printable editions are under [output/pdf](output/pdf). The remaining live checks include longer sessions, Stack-Up Memory/Bingo, Nestopia Game A gate return, and simultaneous browser clients.

Historical Nintendo manuals and the Robert project informed behavior, but their text or code is not reused here. Nintendo's characters, game artwork, and marks remain with their owners. R.O.B. Vision is not affiliated with or endorsed by Nintendo.
