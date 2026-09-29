# Install and set up R.O.B. Vision

Install R.O.B. Vision on your UNO Q and console, pair them, then try your first game. **Installation and upgrades use the same command on each device.** Upgrades keep your saved pairing and game filenames.

## Before you begin

You need an Arduino UNO Q with App Lab, a RetroPie, Batocera, or Recalbox console, a physical gamepad configured in EmulationStation, and your own Gyromite or Stack-Up game files. Put both devices on the same trusted network and connect them to the internet for installation.

Exit any running game. On RetroPie, also exit EmulationStation to its terminal before installing: replacing virtual controllers while the game menu is open can make it crash.

The installer checks the required tools and emulator support. If it reports a missing requirement, follow that message and rerun the same command. Detailed platform requirements are in the [Configuration Reference](CONFIGURATION_REFERENCE.md).

## 1. Install or upgrade the UNO Q

In the UNO Q terminal, signed in as `arduino`, install the app:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/latest/download/install.sh | sh -s -- uno-q
```

Leave the terminal open until installation finishes. The first shared Matrix build may take several minutes.

The installer prints links using both the UNO Q's `.local` name and LAN IP address. Open its **Setup** link on your computer, tablet, or phone.

Controller Router is included. Visiting the UNO Q address opens R.O.B. Vision when it is the only controller app installed, or shows the app chooser when VirtualGlove is installed too. **Apps** returns to the chooser. Both apps stay available; finish a game before changing apps manually.

## 2. Install or upgrade the console

In the console terminal, signed in as `pi` on RetroPie or `root` on Batocera or Recalbox, install the console software:

```sh
curl -fsSL https://github.com/mathan416/ROB-Vision/releases/latest/download/install.sh | \
  sh -s -- console your-uno-q.local
```

Replace `your-uno-q.local` with the UNO Q name or IP address printed by its installer. The same command detects RetroPie, Batocera, or Recalbox and includes Controller Router and the game integration. The currently tested Recalbox combination is 10.1.1 on the `rpizero2` target; another target needs its matching packaged frame wrapper.

For a new pairing, the installer prints a single-use **CR1 connection code**. Use it within five minutes. An upgrade keeps the existing connection.

## 3. Pair the console

Pair once for the UNO Q and console. VirtualGlove and R.O.B. Vision receive their own private credentials automatically when installed on both devices. Installing the other app later adds its access without another pairing. No SSH username or password is required.

Finish the game before pairing, changing app access, or removing a connection. Each console connects to one UNO Q at a time. Connecting it to another requires a new console code and Matrix confirmation.

1. Open **Apps > Setup > Pair console**. Both product Setup pages have an **Open Pair console** link to this same page.
2. Open the secure address printed by the UNO Q installer, using its `.local` name or LAN IP. Pairing uses HTTPS port **8444**.
3. Before accepting the local certificate, compare the browser's SHA-256 fingerprint with the fingerprint printed by the UNO Q installer. During confirmation, its beginning also appears after **ID** on the Matrix. Stop if they differ.
4. Enter the console hostname or IP address and paste its complete **CR1 connection code**. The console installer prints this single-use code; it lasts five minutes.
5. Choose **Continue**, read the six Matrix digits after **PN**, and enter them within two minutes.
6. Choose **Connect**. Wait for **Connected** and check each app's readiness below it.

Buddy is assigned to Player 2. Existing physical-controller assignments stay saved. No further terminal command is needed.

## 4. Check players and game filenames

1. Open **Setup** from the Controller Router page at the UNO Q address.
2. Select your console and check **Players**. Keep your physical gamepad on Player 1; Buddy stays on Player 2.
3. Under **Systems**, keep **Controller Router** enabled for NES. Other systems can use **My existing setup** if you prefer your normal controls.
4. With the game closed, choose **Save assignments** if you changed anything.
5. In R.O.B. Vision Setup, choose **Edit ROMs** beside the console if your filename differs from the supplied entries.

The [Setup Guide](SETUP_GUIDE.md#register-your-game-filenames) explains how to add a filename. The [Controller Router Guide](CONTROLLER_ROUTER.md) explains pad tests and system choices.

## 5. Try your first game

1. Launch Gyromite or Stack-Up. On RetroPie, use **lr-robvision-fceumm** or **lr-robvision-nestopia**. Batocera and Recalbox select the installed R.O.B. Vision core for registered games.
2. Open Mission and look for the correct game and **GAME FRAMES LINKED**.
3. Enter the game's **Test** mode. Buddy's red light should blink and the UNO Q should show **T**.
4. Enter **Direct** mode and send a movement command. Watch Buddy respond.
5. For Gyromite, enter **Game A** and try one colored gate with Setup's **Lower Blue** or **Lower Red**, then **Release Both**.

Starting a registered game selects Buddy's controller automatically. A browser is optional for sending game commands, but keep Mission open to see Buddy's pieces and position.

## Upgrade, repair, or pair again

To upgrade or repair, close games and repeat the same installation command on each device. Keep the printed backup paths until you have checked a game. Upgrades keep your pairings, filenames, and player assignments.

If you removed a console in Setup, add `--pair` to the end of its console command to open a new pairing window. Choose **Pair console** in Router Setup to add another machine. Each console connects to one UNO Q at a time.

See the [Game Manual](GAME_MANUAL.md) for playing, or [Troubleshooting](TROUBLESHOOTING.md) if a check does not work.
