# R.O.B. Vision

R.O.B. Vision is a frame-driven virtual robot companion for Gyromite and Stack-Up. A supported console wrapper reads the games' rendered light commands from FCEUmm or Nestopia frames and sends them to an Arduino UNO Q controller. The controller updates Buddy's virtual movements and game pieces on the Mission page. Gyromite gate actions return to the console as Player 2 input. The system does not require a camera or physical robot.

| Component | Runs on | Function |
| --- | --- | --- |
| Frame wrapper and receiver | RetroPie, Batocera, or Recalbox | Decode game frames, authenticate the link, and provide game and controller state |
| R.O.B. Vision service | UNO Q | Interpret commands, maintain Buddy's state, and serve Mission and Setup |
| Controller Router | UNO Q and console | Pair the console, reserve Player 2, arbitrate input, and own the shared Matrix display |
| Buddy skin | Browser | Render the selected visual skin without changing game or input state |

[Meet Buddy](docs/MEET_BUDDY.md), [see the Mission page](dashboard/index.html), or [print a desk-sized Buddy](models/buddy/README.md). The companion [public website](website/README.md) is a separate static site for manual publishing.

The stable release is **v0.3.0**. See the [release notes](docs/RELEASE_NOTES_0.3.0.md) for changes and qualification scope. Release candidate **v0.3.1-rc.3** adds pairing security fixes, Matrix confirmation for console changes, and a lower console CPU load; see the [0.3.1 notes](docs/RELEASE_NOTES_0.3.1.md).

The release bundles Controller Router 0.3.0 and its independently versioned UNO Q portal 0.3.3. Use the installation guide packaged with the version you install; GitHub's `releases/latest` URL selects a stable release, not a prerelease.

## Install or upgrade

The **same command** installs or upgrades each device. Close any game first. On RetroPie, exit EmulationStation to its terminal before replacing controller software. The controller needs Arduino App Lab; the console needs a working physical gamepad and your own Gyromite or Stack-Up game file.

On the controller, signed in as `arduino`:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/latest/download/install.sh | sh -s -- uno-q
```

On RetroPie as `pi`, or Batocera or Recalbox as `root`, replace the address with the name or IP printed by the controller installer:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/latest/download/install.sh | \
  sh -s -- console your-controller.local
```

These commands install the **latest published stable release**. A prerelease requires its versioned installer. On the UNO Q, follow the installer's printed `NEXT` command for the privileged boot-order helper; an existing rule is checked without changing it. See [Install and set up R.O.B. Vision](docs/INSTALLATION_AND_SETUP.md) for platform checks, repair, and first-game verification.

## Connect and play

Controller Router is included with R.O.B. Vision and owns the shared Matrix display. Its port-80 page opens R.O.B. Vision directly if it is the sole installed app, or shows **Apps** when VirtualGlove is installed too. Both app services remain available. A registered game selects its app automatically; keeping a browser open is optional for input.

Pair the console once by choosing **Pair console** from Apps. The console installer opens a short connection window and prints a one-time code. The secure pairing page checks the console identity and asks for confirmation from the controller's Matrix display. Router provisions separate credentials for each installed app. The [Controller Router Pairing Guide](controller_router_portal/python/guides/Controller-Router-Pairing-Guide.pdf) explains the steps.

Check **Players and Systems** after pairing. Buddy belongs on Player 2; keep a physical pad on Player 1 and enable Router for NES. In R.O.B. Vision Setup, choose **Edit ROMs** beside a paired console if your game's filename differs from the supplied registry entries. The registry is saved on that console and survives upgrades.

Launch a registered game using its R.O.B. Vision emulator choice. On RetroPie these are `lr-robvision-fceumm` and `lr-robvision-nestopia`; ordinary `lr-fceumm` and `lr-nestopia` do not send Buddy's movement frames. The [Setup page](dashboard/setup.html) shows console and frame-link status, tests the controls, and lets you edit filenames. [Mission](dashboard/index.html) shows Buddy in motion, and [Help](dashboard/help.html) gives task-based play and recovery steps. The current app site uses port **8101**; the console receiver uses **8766**.

In Gyromite, a gyro placed on a coloured pad or a **Fast Gates** hold sends the matching button to Player 2. In Stack-Up, the game-frame link drives Buddy's movement and block handling. The Test signal lights his status indicator without moving him. When no game is active, a demo can run even while a console remains paired.

## Guides and source

- [Installation and Setup](docs/INSTALLATION_AND_SETUP.md) and [Setup Guide](docs/SETUP_GUIDE.md) cover first use, filenames, and recovery.
- [Game Manual](docs/GAME_MANUAL.md) and [User Guide](docs/USER_GUIDE.md) explain play.
- [Technical Reference](docs/TECHNICAL_ARCHITECTURE.md), [Technical Test Results](docs/TEST_RESULTS_TECHNICAL.md), and [Engineering Journey](docs/ENGINEERING_JOURNEY.md) document the design and its evidence.
- [Buddy & the Big Wide Window](docs/BUDDY_ADVENTURE.md) tells Buddy's story.

Printable guides are in [output/pdf](output/pdf/). The dashboard serves its own Help and guide downloads. R.O.B. Vision includes no ROMs or pairing credentials in this repository. It is an independent maker project and is not affiliated with Nintendo; see the [license](LICENSE) and [third-party components](docs/THIRD_PARTY_COMPONENTS.md).

## Validate a deployment

After installation, check that the console is paired, the frame-link status is ready, and Buddy responds in Mission while a registered game is running. Confirm that the physical Player 1 pad still works, Gyromite gate actions reach Player 2, and exit controls release both inputs. Keep the installer's recovery backup until those checks pass. A package or CI pass does not establish the behavior of every emulator build and physical setup.

## Continuous integration

Pushes to `dev`/`main` and pull requests run the full Python suite on the controller's Python 3.9 minimum and Python 3.12. A separate Python 3.7 job tests the RetroPie receiver, shared Router, pairing and configuration-preservation contracts. Dashboard tests run with Node.js 22, alongside shell entrypoint syntax checks. These jobs run for Router changes as well as application changes; the existing optional emulator-wrapper build remains separate.

Run the full suite locally with `python3 -m unittest discover -s tests -v` and `node --test tests/*.test.js`. Tests use temporary configuration and mocked devices; CI does not connect to or deploy onto a console.
