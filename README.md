# R.O.B. Vision

R.O.B. Vision brings Buddy, a virtual robot companion, into Gyromite and Stack-Up. A supported RetroPie, Batocera, or Recalbox console sends the games' rendered light commands through an FCEUmm or Nestopia frame wrapper. The controller turns those commands into Buddy's movements; Mission shows him and the game pieces in a browser. Gyromite's red and blue gate buttons return to the console as Player 2 input. No camera or physical robot is needed.

[Meet Buddy](docs/MEET_BUDDY.md), [see the Mission page](dashboard/index.html), or [print a desk-sized Buddy](models/buddy/README.md). The companion [public website](website/README.md) is a separate static site for manual publishing.

This README describes the current development checkout. The published stable installer may contain an earlier version of Controller Router and its pairing interface. Use the installation guide distributed with the release you install; GitHub's `releases/latest` URL does not select prereleases.

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

These commands install the **latest published stable release**. For this development checkout or a release candidate, follow that candidate's versioned installation instructions. See [Install and set up R.O.B. Vision](docs/INSTALLATION_AND_SETUP.md) for current-source requirements, platform checks, repair, and first-game verification.

## Connect and play

In the current development version, Controller Router is included with R.O.B. Vision and owns the shared Matrix display. Its port-80 page opens R.O.B. Vision directly if it is the sole installed app, or shows **Apps** when VirtualGlove is installed too. Both app services remain available. A registered game selects its app automatically; keeping a browser open is optional for input.

Pair the console once by choosing **Pair console** from Apps. The console installer opens a short connection window and prints a one-time code. The secure pairing page checks the console identity and asks for confirmation from the controller's Matrix display. Router provisions separate credentials for each installed app. The [Controller Router Pairing Guide](controller_router_portal/python/guides/Controller-Router-Pairing-Guide.pdf) explains the steps.

Check **Players and Systems** after pairing. Buddy belongs on Player 2; keep a physical pad on Player 1 and enable Router for NES. In R.O.B. Vision Setup, choose **Edit ROMs** beside a paired console if your game's filename differs from the supplied registry entries. The registry is saved on that console and survives upgrades.

Launch a registered game using its R.O.B. Vision emulator choice. On RetroPie these are `lr-robvision-fceumm` and `lr-robvision-nestopia`; ordinary `lr-fceumm` and `lr-nestopia` do not send Buddy's movement frames. The [Setup page](dashboard/setup.html) shows console and frame-link status, tests the controls, and lets you edit filenames. [Mission](dashboard/index.html) shows Buddy in motion, and [Help](dashboard/help.html) gives task-based play and recovery steps. The current app site uses port **8101**; the console receiver uses **8766**.

In Gyromite, a gyro placed on a colored pad or a **Fast Gates** hold sends the matching button to Player 2. In Stack-Up, the game-frame link drives Buddy's movement and block handling. The Test signal lights his status indicator without moving him. When no game is active, a demo can run even while a console remains paired.

## Guides and source

- [Installation and Setup](docs/INSTALLATION_AND_SETUP.md) and [Setup Guide](docs/SETUP_GUIDE.md) cover first use, filenames, and recovery.
- [Game Manual](docs/GAME_MANUAL.md) and [User Guide](docs/USER_GUIDE.md) explain play.
- [Technical Reference](docs/TECHNICAL_ARCHITECTURE.md), [Technical Test Results](docs/TEST_RESULTS_TECHNICAL.md), and [Engineering Journey](docs/ENGINEERING_JOURNEY.md) document the design and its evidence.
- [Buddy & the Big Wide Window](docs/BUDDY_ADVENTURE.md) tells Buddy's story.

Printable guides are in [output/pdf](output/pdf/). The dashboard serves its own Help and guide downloads. R.O.B. Vision includes no ROMs or pairing credentials in this repository. It is an independent maker project and is not affiliated with Nintendo; see the [license](LICENSE) and [third-party components](docs/THIRD_PARTY_COMPONENTS.md).
