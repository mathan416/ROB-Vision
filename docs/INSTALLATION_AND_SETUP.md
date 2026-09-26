# Install and set up R.O.B. Vision

This guide gets a new Arduino UNO Q and one RetroPie or Batocera console ready to play. R.O.B. Vision runs Buddy and the virtual game pieces on the UNO Q; your browser shows them. The console runs the NES game and sends its rendered light commands over your local network. You can pair more than one console, but only one game session is active at a time.

## What you need

- An Arduino UNO Q with App Lab, plus a RetroPie console with the `pi` account or a Batocera 43.1 x86_64 console with the `root` account. Other Batocera boards and versions are checked and reported as unsupported before installation.
- Both devices on the same trusted network. The UNO Q needs Python 3.9+; standard RetroPie needs Python 3.7+, `gcc`, `openssl`, `sudo`, systemd, `uinput`, and at least one installed NES core (`lr-fceumm` or `lr-nestopia`).
- `curl`, `tar`, Python 3, and `sha256sum` or `shasum` on the device running each installer command. The installer reports missing prerequisites.
- Your own legally obtained Gyromite or Stack-Up ROM. The console identifies the game by an exact registered NES ROM filename; see [game identification](GAME_IDENTIFICATION.md).

Before installing on RetroPie, exit any game **and EmulationStation**. Restarting the virtual joystick while EmulationStation is open can crash its input manager. On the UNO Q, stop another App Lab app before starting R.O.B. Vision.

## 1. Install on the UNO Q

Sign in as `arduino` and run this command in its terminal:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/download/v0.1.6/install.sh | sh -s -- uno-q
```

The installer verifies the release package, installs and starts the App Lab app, and compiles and uploads the LED matrix sketch. It prints Mission and Setup links for both the UNO Q's `.local` name and available LAN IPv4 addresses. Open the printed **Setup** link in a browser on your laptop, tablet, or phone. A downloaded `file://` copy of Setup is only a preview and cannot pair a live console.

## 2. Install on each console

Run this command **on RetroPie or Batocera**, replacing `your-uno-q.local` with the UNO Q name or LAN IP printed by its installer:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/download/v0.1.6/install.sh | \
  sh -s -- console your-uno-q.local
```

The same command detects the platform. It installs the game-frame integration, local receiver, launch and exit detection, and virtual Controller 2. On Batocera, it temporarily pauses and resumes the game menu while updating the virtual joystick. On RetroPie, it requires EmulationStation to be closed. It does not install ROMs.

For a first install, leave the terminal open. The installer prints a **six-digit pairing code** and a **SHA-256 certificate fingerprint**, and waits up to five minutes. Do not enter a password or private key in Setup.

## 3. Pair in Setup

On the UNO Q Setup page, open **Console Link**. Enter the console address, the six-digit code, and the fingerprint exactly as printed. Choose **Pair Console**. Wait until the console terminal says **Pairing complete**, then select **Check Link** in Setup. The receiver starts and Gyromite's virtual Player 2 is configured automatically.

Use **Pair Another Console** for a second machine. Paired consoles appear as separate rows. **Remove** and **Confirm Remove** revoke one console without unpairing the others. To reconnect a removed console, rerun its one-command install with `--pair` appended.

## 4. Check a game

On RetroPie, launch the exact registered Gyromite or Stack-Up ROM with `lr-robvision-fceumm` or `lr-robvision-nestopia`. On supported Batocera, launching a registered ROM selects its R.O.B. Vision wrapper; an existing supported Nestopia choice can be retained. An ordinary NES core still plays the game but does not send Buddy commands.

Mission and Setup should show the game selected and **GAME FRAMES LINKED**. In Test mode, Buddy's red light blinks automatically and the UNO Q matrix shows **T**. In Gyromite Game A, use **Lower Blue** and **Lower Red** separately to check the gates, then **Release Both**. In Stack-Up Direct mode, move Hector onto a command key and watch Buddy and the blocks on Mission.

If the link is online but no game is selected, check the exact ROM filename and launch the game again. If the game is selected but frames are waiting, check the R.O.B. Vision core choice. The built-in Help and [Troubleshooting](TROUBLESHOOTING.md) give the next checks.

## Upgrade or repair

Rerun the same install command on the device you are upgrading. The UNO Q app restarts while preserving pairing data; the console retains its credential and restarts its receiver. Exit an active RetroPie game and EmulationStation before reinstalling. The installer verifies the downloaded source package before changing installed files. Release packages also publish `SHA256SUMS`.

For advanced configuration and platform-specific service details, see the [Technical Reference](TECHNICAL_ARCHITECTURE.md), [RetroPie deployment](../deploy/retropie/README.md), and [Batocera deployment](../deploy/batocera/README.md).
