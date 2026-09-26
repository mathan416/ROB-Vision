# R.O.B. Vision installation guide — 0.1.0

R.O.B. Vision runs on an Arduino UNO Q and connects to either RetroPie or Batocera. Install the UNO Q first, then install each console. The release installer downloads a versioned source package, checks its SHA-256 digest, and runs the platform installer. No Git checkout, ROM transfer, or SSH transfer is required.

## Before you begin

- Connect the UNO Q and console to the same trusted network. Sign in to the UNO Q as `arduino`, to RetroPie as `pi`, or to Batocera as `root`.
- Install UNO Q App Lab. Standard RetroPie needs Python 3.7+, `gcc`, `openssl`, `sudo`, systemd, `uinput`, and at least one installed NES core (`lr-fceumm` or `lr-nestopia`). The UNO Q needs Python 3.9+. Batocera 43.1 x86_64 is the validated Batocera target; the command checks the board and version before installation.
- Exit any running game and EmulationStation on RetroPie. Restarting the virtual joystick while EmulationStation is open can crash its input manager. Stop a different App Lab app before installing R.O.B. Vision. Supply your own legally obtained Gyromite or Stack-Up ROM with an exact name in `config/games.json`.
- `curl`, `tar`, Python 3, and either `sha256sum` or `shasum` are needed to run the single-command download. The installer reports a missing prerequisite before installing.

## Install the UNO Q

Run this one command in the UNO Q terminal as `arduino`:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/download/v0.1.0/install.sh | sh -s -- uno-q
```

The command downloads and verifies R.O.B. Vision, installs the separate App Lab app, and starts it. On upgrades, App Lab stops and restarts the app while preserving its pairing data. The installation includes the UNO Q matrix sketch; App Lab compiles and uploads that sketch when starting the app. It does not replace the board's bootloader or firmware. Open `http://<your-uno-q-hostname>.local/dashboard/setup.html` in a browser on the same network. `http://arduiain.local/dashboard/setup.html` is the address of the project's test UNO Q.

## Install a console

Run this one command **on RetroPie or Batocera**, replacing `your-uno-q.local` with your UNO Q's LAN hostname or IP address:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/download/v0.1.0/install.sh | \
  sh -s -- console your-uno-q.local
```

The command detects the console. On RetroPie it uses `sudo` for system changes and requires EmulationStation to be closed. On Batocera it runs under the root login and temporarily suspends and resumes its game menu while the virtual joystick is restarted. It installs the frame wrappers, receiver, game launch integration, and Gyromite's virtual Controller 2. For a first install it opens a five-minute pairing window and prints a six-digit code and SHA-256 certificate fingerprint. Enter the console's hostname, code, and fingerprint under **Console Link** on the UNO Q Setup page. Keep the console command open until it reports **Pairing complete**. Successful pairing starts the receiver and maps RetroPie's Player 2 automatically. No second terminal command is required.

<!-- pagebreak -->

## Upgrades and re-pairing

An upgrade retains that console's credential and restarts its receiver. Rerun the same command for a repair or upgrade. If you remove a console in Setup, rerun the console command with `--pair` added at the end to open a new pairing window; this is still one command on the console.

The installer leaves ROM files and unrelated games alone. RetroPie registers `lr-robvision-fceumm` and `lr-robvision-nestopia` for the exact registered ROM names. Batocera selects its R.O.B. Vision FCEUmm wrapper for those names while retaining unrelated core choices. Plain NES cores still play games but do not send commands to R.O.B. Vision.

## Check the link and play

On Setup, select **Check Link** after pairing. It should show the console online. Launch Gyromite or Stack-Up using a R.O.B. Vision core; Mission and Setup should show **GAME FRAMES LINKED**. In Gyromite Test mode the matrix Test light blinks automatically. In Game A, test blue and red gates independently. Stack-Up Direct mode supplies Left, Right, Up, Down, Open, and Close. The virtual robot and game pieces appear in Mission on a laptop, phone, or tablet. A camera and physical robot are not required.

If a game is already running during installation, the console installer stops before changing its configuration. Exit the game and run the same command again. An unsupported Batocera board or version is reported before any changes. For a failed link, see [Troubleshooting](TROUBLESHOOTING.md) and the built-in Help page.

## Supported releases and integrity

Version 0.1.0 validates UNO Q App Lab, standard RetroPie with the `pi` account, and Batocera 43.1 x86_64. Other Batocera boards are detected by the same command and rejected until their core libraries and gameplay pass validation. Release assets include the source package, installer, PDFs, and `SHA256SUMS`. The installer pins the source package's digest; the checksum file also lets you check downloaded assets independently. The repository contains no ROMs.

For development or repair, the [RetroPie](../deploy/retropie/README.md) and [Batocera](../deploy/batocera/README.md) guides document individual components. The normal install path is the one command above for each device, followed by browser pairing.
