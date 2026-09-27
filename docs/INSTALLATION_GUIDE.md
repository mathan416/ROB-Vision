# R.O.B. Vision installation guide — 0.1.7

R.O.B. Vision runs on an Arduino UNO Q and connects to either RetroPie or Batocera. Install the UNO Q first, then install each console. **Each device has one command for both installation and upgrades.** Rerun that device's command to get the latest release; there is no separate upgrade command. The release installer downloads and verifies the app before installing it.

## Before you begin

- Connect the UNO Q and console to the same trusted network. Sign in to the UNO Q as `arduino`, to RetroPie as `pi`, or to Batocera as `root`.
- Install UNO Q App Lab. Standard RetroPie needs Python 3.7+, `gcc`, `openssl`, `sudo`, systemd, `uinput`, and at least one installed NES core (`lr-fceumm` or `lr-nestopia`). The UNO Q needs Python 3.9+. Batocera needs Python 3.9+, its service manager, SDL2, and an installed FCEUmm or Nestopia core. The installer uses a matching packaged frame wrapper or compiles one when a native C compiler is available.
- Exit any running game and EmulationStation on RetroPie. Restarting the virtual joystick while EmulationStation is open can crash its input manager. Stop a different App Lab app before installing R.O.B. Vision. Supply your own legally obtained Gyromite or Stack-Up ROM. After pairing, select **Edit ROMs** beside that console in Setup to add a different filename to its registry.
- `curl`, `tar`, Python 3, and either `sha256sum` or `shasum` are needed to run the single-command download. The installer reports a missing prerequisite before installing.

## Install or upgrade the UNO Q

Run this one command in the UNO Q terminal as `arduino`:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/latest/download/install.sh | sh -s -- uno-q
```

Use this exact command again to upgrade or repair the UNO Q. It downloads and verifies the latest R.O.B. Vision release, installs the App Lab app, and starts it. On upgrades, App Lab stops and restarts the app while preserving its pairing data. App Lab also compiles and uploads the UNO Q matrix sketch. At the end, the installer prints Mission and Setup links using the device's `.local` name and available LAN IPv4 addresses. Open either form in a browser on the same network.

## Install or upgrade a console

Run this one command **on RetroPie or Batocera**, replacing `your-uno-q.local` with your UNO Q's LAN hostname or IP address:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/latest/download/install.sh | \
  sh -s -- console your-uno-q.local
```

Use this exact command again to upgrade or repair that console. It detects RetroPie or Batocera. On RetroPie it uses `sudo` for system changes and requires EmulationStation to be closed. On Batocera it runs under the root login and temporarily suspends and resumes its game menu while the virtual joystick is restarted. It installs the frame wrappers, receiver, game launch integration, and Controller Router with Buddy assigned to Player 2. For a first install it opens a five-minute pairing window and prints a six-digit code and SHA-256 certificate fingerprint. Enter the console's `.local` hostname or LAN IP address, code, and fingerprint under **Console Link** on the UNO Q Setup page. Keep the console command open until it reports **Pairing complete**. Successful pairing starts the receiver, installs or updates Controller Router, and assigns Buddy to Player 2. Existing physical-controller assignments remain in place. No second terminal command is required.

<!-- pagebreak -->

## Upgrades and re-pairing

An upgrade retains that console's credential and restarts its receiver. Rerun the command in **Install or upgrade a console** for a repair or upgrade. If you remove a console in Setup, rerun the console command with `--pair` added at the end to open a new pairing window; this is still one command on the console.

The installer leaves ROM files and unrelated games alone. RetroPie registers `lr-robvision-fceumm` and `lr-robvision-nestopia` for the exact registered ROM names. Batocera selects its R.O.B. Vision FCEUmm wrapper for those names while retaining unrelated core choices. Plain NES cores still play games but do not send commands to R.O.B. Vision.

## Review controller assignments

On the UNO Q Setup page, choose **Controllers** beside a paired console. Buddy stays on Player 2. The list shows physical controllers configured in EmulationStation and their current player assignments. On a new Router installation, known controllers are seeded in Player 1-4 order. Change an assignment if needed, exit the running game, and choose **Save Assignments**. **Test Inputs** listens briefly for buttons and directions. **Restore Previous** returns to the last saved assignment. RetroPie requires EmulationStation closed during first pairing or Router installation because new virtual controllers can upset its input manager.

## Check the link and play

On Setup, select **Check Link** after pairing. It should show the console online. Launch Gyromite or Stack-Up using a R.O.B. Vision core; Mission and Setup should show **GAME FRAMES LINKED**. In Gyromite Test mode the Test light blinks automatically. In Game A, test blue and red gates independently. Stack-Up Direct mode supplies Left, Right, Up, Down, Open, and Close. The virtual robot and game pieces appear in Mission on a laptop, phone, or tablet.

If a game is already running during installation, the console installer stops before changing its configuration. Exit the game and run the same command again. On Batocera, missing NES cores or a usable native wrapper are reported before any changes. For a failed link, see [Troubleshooting](TROUBLESHOOTING.md) and the built-in Help page.

## Supported releases and integrity

The Batocera installer checks installed NES cores and a loadable frame wrapper rather than a fixed board or version. The package includes FCEUmm and Nestopia wrappers for x86_64, 32-bit x86, AArch64, ARMv7, ARMv6, and RISC-V 64. If a packaged wrapper cannot load, a native C compiler can build one before installation changes the device. Live device testing covered Batocera 43.1 x86_64; other architectures receive the same preflight checks but have not all been tested on physical hardware. Release assets include the source package, installer, PDFs, and `SHA256SUMS`. The installer checks the source package's digest before installing it.

For advanced repair, see the [RetroPie](../deploy/retropie/README.md) and [Batocera](../deploy/batocera/README.md) guides.
