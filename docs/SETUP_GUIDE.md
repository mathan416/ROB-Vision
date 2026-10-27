# Get Buddy ready to play

Use R.O.B. Vision **Setup** to pair a console, register your game filenames, and check Buddy's controls. Open R.O.B. Vision at your UNO Q address, then choose **Setup**.

Installing for the first time? Start with [Installation and Setup](INSTALLATION_AND_SETUP.md).

## Pair a console

Pair once for the UNO Q and console. VirtualGlove and R.O.B. Vision receive their own private credentials automatically when installed on both devices. Installing the other app later adds its access without another pairing. No SSH username or password is required.

Finish the game before pairing, changing app access, or removing a connection. Each console connects to one UNO Q at a time. Connecting it to another requires a new console code and Matrix confirmation.

1. Open **Apps > Setup > Pair console**. Both product Setup pages have an **Open Pair console** link to this same page.
2. Open the secure address printed by the UNO Q installer, using its `.local` name or LAN IP. Pairing uses HTTPS port **8444**.
3. Before accepting the local certificate, compare the browser's SHA-256 fingerprint with the fingerprint printed by the UNO Q installer. During confirmation, its beginning also appears after **ID** on the Matrix. Stop if they differ.
4. Enter the console hostname or IP address and paste its complete **CR1 connection code**. The console installer prints this single-use code; it lasts five minutes.
5. Choose **Continue**, read the six Matrix digits after **PN**, and enter them within two minutes.
6. Choose **Connect**. Wait for **Connected** and check each app's readiness below it.

### Check or repair a connection

Open **Pair console > Your consoles**. **Connected** means Router has verified the console connection. **Unavailable** means it could not reach the console. **Needs attention** means the certificate, identity, or app setup needs review. App readiness is shown separately.

Choose **Check and repair connections** after reconnecting a device or installing another app. Use **Disable** beside an app to remove only its access, or **Remove console** to remove the whole connection. Finish any game first. A certificate change requires a fresh pairing; do not ignore the mismatch.

For another code, rerun the console installer or its pairing command. Existing game filenames and player assignments remain saved. Incorrect, expired, or already-used codes require a new window; five incorrect Matrix confirmations lock the current window.

## Register your game filenames

If your game has a different filename from the supplied entries, add it to that console's registry.

1. Exit the game.
2. In **Console Link**, choose **Edit ROMs** beside the console.
3. In the **Game Registry** editor, find the `games` section.
4. Add the game's exact filename, including its extension, with `gyromite` or `stack_up` as its value.
5. Choose **Validate**, then **Save to Console**.
6. Launch the game again.

For example, an entry for your own Gyromite ZIP can look like this:

```json
"My Gyromite.zip": "gyromite"
```

Add the entry inside the existing `games` object and keep the other entries. Each console has its own registry. Changes and upgrades keep your saved filenames.

## Check the game connection

1. On RetroPie, launch the game with **lr-robvision-fceumm** or **lr-robvision-nestopia**. On Batocera or Recalbox, launch the registered game; the installer selects its R.O.B. Vision core.
2. In Setup, check that the correct game is shown.
3. Look for **GAME FRAMES LINKED**.
4. Send one movement command from the game and watch Buddy on Mission.

**GAME FRAMES LINKED** means game signals are reaching R.O.B. Vision. A blocked movement is explained in Mission's **Activity Feed**.

## Try the game's Test mode

1. Enter **Test** in the game. In Stack-Up, press Select on the ROBOT BLOCK screen, choose Test, then press Start.
2. Watch Buddy's red light on Mission or Setup. It should blink automatically.
3. Check the UNO Q display for a pulsing **T**.

Test checks the connection without moving Buddy. A brief steady red light acknowledges the game's ready signal. **Preview Red Light** lets you try the animation yourself; it does not check the game connection.

## Check Gyromite's gates

1. Enter Gyromite **Game A** and leave a coloured gate visible.
2. In Setup, choose **Lower Blue** or **Lower Red** for that gate.
3. Watch the game screen for the gate to move.
4. Choose **Release Both** when finished.

Choose a colour again to release it. A hold also releases after 60 seconds. If a gyro is already in use, return it with the normal controls or choose **Home** to reset the pieces before using Fast Gates.

## Check Stack-Up movement

In Setup, try **Left**, **Right**, **Up**, **Down**, **Open**, or **Close** one at a time. Watch Mission's Live Model and Game Table. Raise Buddy's hands before moving sideways past a stack. A blocked move keeps the pieces intact; read the Activity Feed, raise the hands, and try again.

## Remove a console

Open **Apps > Setup > Pair console**, find the console under **Your consoles**, and choose **Remove console**. Removing it revokes both apps’ access. To remove only Buddy’s access, choose **Disable R.O.B. Vision** instead.

For physical gamepads and Buddy's Player 2 controls, see the [Controller Router Guide](CONTROLLER_ROUTER.md). For game rules and pieces, see the [Game Manual](GAME_MANUAL.md).
