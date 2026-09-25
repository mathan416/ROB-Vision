# R.O.B. Vision installation guide

**Installed test setup, 25 September 2026:** R.O.B. Vision is a separate UNO Q App Lab app. `retropie.local` has exact-name launch/exit hooks, pairing, a virtual Controller 2 receiver, and FCEUmm and Nestopia frame-link choices. Gyromite launch/exit and both gate colors were verified under FCEUmm. Both games delivered commands through FCEUmm and Nestopia. Nestopia's Gyromite Player 2 gate return still needs a Game A check. There is no physical robot or camera. The installer below is a development preview. It passed local tests and live in-place upgrades on both devices, but a fresh installation on two new devices has not yet been run.

## Before you begin

- Use an Arduino UNO Q with App Lab and either standard RetroPie with the `pi` account and `/opt/retropie/configs`, or Batocera 43.1 x86_64. The UNO Q needs Python 3.9 or newer; RetroPie needs Python 3.7 or newer. Direct cloning needs `git` on each device; the SSH archive transfer below does not. RetroPie also needs `gcc`, `openssl`, `modprobe`, systemd, and at least one installed NES libretro core: `lr-fceumm` or `lr-nestopia`.
- Supply your own legally obtained Gyromite or Stack-Up ROM with an exact filename listed in `config/games.json`. The repository and installer contain no ROMs.
- Keep both devices on a trusted local network. Exit any NES game before installation or upgrade. The UNO Q installer stops and restarts R.O.B. Vision automatically; stop any other App Lab app first. The UNO Q can run only one App Lab app at a time on the tested device.
- The GitHub repository is currently private. A direct clone on a device requires a GitHub account with access and authenticated Git on that device. You can instead send the source from an authorized computer over SSH without copying GitHub credentials to either device.

For the SSH transfer option, run these commands **on a computer with a local checkout of `dev`**, replacing the device names. They create only the source folders used by the installer:

```sh
git archive --format=tar dev | ssh arduino@your-uno-q.local 'mkdir -p /home/arduino/rob-vision-src && tar -xf - -C /home/arduino/rob-vision-src'
git archive --format=tar dev | ssh pi@your-retropie.local 'mkdir -p /home/pi/rob-vision-src && tar -xf - -C /home/pi/rob-vision-src'
```

Then skip each `git clone` command below and run its installer command. For an upgrade using this option, transfer the new archive again before rerunning the installer.

## Install on the UNO Q

As the `arduino` user, clone the development branch outside the App Lab app folder and run:

```sh
git clone --branch dev https://github.com/mathan416/ROB-Vision.git ~/rob-vision-src
python3 ~/rob-vision-src/scripts/install.py uno-q
```

The installer stages the app in `~/ArduinoApps/rob-vision`, including its `sketch/sketch.ino` matrix-display program. It creates a private controller token on first installation and preserves the token and other app data on upgrade. It stops the running R.O.B. Vision app, installs the new version, starts it through App Lab, and waits for the controller to respond. App Lab compiles and uploads the display sketch when it starts the app; this does not replace the UNO Q's board firmware or bootloader. The installer retains the prior app in a `rob-vision.previous*` sibling for rollback. If the new app fails to start, it restores and restarts the previous version. The normal panel address is `http://<your-uno-q-hostname>.local/dashboard/`; open `/dashboard/setup.html` to pair the console. App Lab owns ports 80 and 8766 while the app runs. Do not enable the separate `deploy/rob-vision.service` at the same time.

On upgrade, the installer also preserves App Lab's `.deps` and `.cache` folders. The previous app directory remains available for rollback until you remove it.

## Install on RetroPie

As `pi`, clone the same branch and run the installer with the UNO Q's LAN hostname or IP:

```sh
git clone --branch dev https://github.com/mathan416/ROB-Vision.git ~/rob-vision-src
sudo python3 ~/rob-vision-src/scripts/install.py retropie --controller your-uno-q.local
```

It installs the root virtual Controller 2 receiver, builds frame wrappers for installed FCEUmm and/or Nestopia cores, and adds two NES launch choices. It selects those choices only for the registered Gyromite and Stack-Up filenames, preserving any unrelated custom emulator choice. Existing runcommand scripts stay in place; the installer adds a marked R.O.B. Vision section near the top and writes a one-time `.before-rob-vision` backup. Its NES config edit is also marked and backed up. It stores the controller address in `/home/pi/.config/rob-vision/receiver.env` and loads `uinput` on future boots. Your ROMs are not copied or changed.

Pair the receiver before starting its service:

```sh
python3 /home/pi/rob-vision/tools/retropie_pair.py
```

Enter the six-digit code and SHA-256 certificate fingerprint in the UNO Q Setup page, then run:

```sh
sudo systemctl enable --now rob-vision-controller2.service
sudo python3 ~/rob-vision-src/scripts/install.py player2
```

The last command discovers **R.O.B. Vision Controller 2** among RetroPie's joysticks and writes its actual index plus the tested red/blue mapping to NES RetroArch configuration. It leaves Player 1 alone. Exit and relaunch Gyromite so RetroArch reads the new mapping. If a joystick order changes later, rerun `player2` while the receiver is running. If you know the index in advance, `retropie --player2-index N` sets it during the initial installation.

In RetroPie's per-game emulator selection, choose `lr-robvision-fceumm` or `lr-robvision-nestopia`. On Setup, **Check Link** should show the receiver online, and launching a registered ROM through a R.O.B. Vision choice should show **GAME FRAMES LINKED**. Start with Gyromite Test, then test blue and red gates individually in Game A. Stack-Up Direct mode can verify each of its six movements. The installer does not reprogram an existing Player 1 controller or its EmulationStation mapping.

To upgrade, exit the games, update each `~/rob-vision-src` checkout, and rerun the corresponding installer. The UNO Q installer handles the App Lab restart. Existing paired consoles are preserved. The console installer restarts the receiver when its credential already exists; no fresh pairing is needed unless that console was removed from Setup or its key changed.

**Live installer check:** On `retropie.local` (Python 3.7), the installer migrated the original standalone hooks, rebuilt both wrappers, preserved the paired token, restarted the receiver, and detected virtual joystick 1. A repeat installation left one managed hook per event and one Controller 2 mapping. Installed launch/end hooks selected and cleared Gyromite and Stack-Up on the UNO Q. The controller reported an authenticated online receiver after the restart. The exact published `dev` archive was transferred over SSH and installed successfully. A direct unauthenticated GitHub clone failed because the repository is private; the check did not run a new gameplay session or exercise first-time pairing on a blank RetroPie.

**UNO Q installer check:** On `arduiain.local` (Python 3.13), an in-place upgrade automatically stopped the running R.O.B. Vision app through App Lab, installed the update, compiled and uploaded the sketch, and restarted the app. Mission, Setup, Help, and controller endpoints returned HTTP 200; `/api/matrix/state` reported an available, connected bridge in idle mode. The pairing token matched the previous app, and RetroPie remained paired and online. Earlier upgrades confirmed that `.deps` and `.cache` survive. Rollback on a failed App Lab start passed an installer test; it has not been forced on the live UNO Q. A blank-device first install remains untested.

## Install on Batocera

On Batocera 43.1 x86_64, copy this checkout to a persistent path outside `/userdata/system/rob-vision`, then run as root while no game is open:

```sh
python3 scripts/install_batocera.py --controller your-uno-q.local
```

The installer enables a separate `ROBVision` service and launch hook, adds bundled x86_64 FCEUmm and Nestopia frame wrappers, and selects FCEUmm for the exact registered ROM filenames. It leaves VirtualGlove's service and Super Glove Ball choice intact. To pair for the first time, run `python3 /userdata/system/rob-vision/tools/retropie_pair.py --platform batocera`, then enter its code and fingerprint on Setup. The service detects the virtual pad and saves **Gyromite-only** RetroArch Player 2 overrides in Batocera's persistent per-ROM settings. Batocera regenerates its live RetroArch config on every launch, so editing `retroarchcustom.cfg` by hand will not persist.

The test Batocera installed and repeated the bundled installer, loaded both wrappers for each game through real launches, selected Stack-Up's FCEUmm wrapper without an explicit core override, retained Gyromite's Player 2 index and A/B mapping after config generation, and showed **Batocera online / game frames linked** on the UNO Q during Stack-Up. A live Batocera gate-response test and full playthrough are still open. See the [Batocera deployment guide](../deploy/batocera/README.md) for core choice and architecture limits.

## UNO Q and browser

Start **R.O.B. Vision** under App Lab **My Apps**. Stop VirtualGlove first because the tested UNO Q runs one App Lab app at a time. App Lab exposes port 80 at `http://<your-uno-q-hostname>.local/dashboard/`; the controller is also reachable on port 8766. Both addresses share one virtual game state. The App Lab `python/main.py` gateway talks to `controller/service.py`, and Router Bridge drives the matrix sketch. Avahi supplies the `.local` hostname when configured on the UNO Q. Keep the separate `deploy/rob-vision.service` disabled while App Lab owns port 8766.

Open [Setup](../dashboard/setup.html) to check pairing and the game-frame link. Browser controls are available on the trusted LAN without a token prompt. New pairings use a separate credential for each console, stored privately in `data/paired-consoles.json` on the UNO Q. The installer's `data/controller-token` remains a migration credential for older paired consoles; an existing `ROB_VISION_TOKEN` environment setting overrides that file. Console Link shows each saved console and can remove it independently. Keep the LAN private. A local `file://` page is an offline preview.

## RetroPie

Follow the [RetroPie deployment instructions](../deploy/retropie/README.md) for the launch/end hooks, root uinput receiver service, pairing, FCEUmm and Nestopia launch choices, and RetroArch port 2 configuration. Merge hooks with any existing scripts rather than replacing unrelated commands. After pairing, **Check Link** turns online when authenticated receiver polls arrive. The receiver can resync game identity from the active RetroArch process after a UNO Q restart.

For Gyromite or Stack-Up, choose `lr-robvision-fceumm` or `lr-robvision-nestopia` in RetroPie's emulator selection. These entries run the installed original core through R.O.B. Vision's frame wrapper. Plain `lr-fceumm` and `lr-nestopia` play without automatic R.O.B. movement. The UNO Q receives only complete game-specific light commands. Setup's Test check uses the same frame link.

## Local development

Run `python3 -m controller.service` and open `http://127.0.0.1:8766/dashboard/`. For trusted-LAN access set `ROB_VISION_TOKEN` and use `--host 0.0.0.0`; the token protects RetroPie traffic, while browser controls are available on that LAN. The static preview can be served with `python3 -m http.server 8000` and has no game link.

Run the [verification plan](VERIFICATION_PLAN.md) before a general release.
