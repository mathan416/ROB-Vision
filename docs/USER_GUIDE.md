# R.O.B. Vision user guide

The UNO Q controls Buddy, the virtual robot shown in Mission. RetroPie or Batocera sends Gyromite and Stack-Up commands through the game-frame link. His movements and game pieces appear in your browser.

## Open R.O.B. Vision

Install R.O.B. Vision with the two commands in the [installation guide](INSTALLATION_GUIDE.md): one on the UNO Q, one on the console. The console command prints first-time pairing details for Setup and configures its receiver automatically.

1. Open your UNO Q's `.local` address or LAN IP in a browser on the same network.
2. If you see the app chooser, choose **R.O.B. Vision**.
3. Open **Mission** to see Buddy, his accessories, and the Game Table.

**Apps** returns to the chooser when both controller apps are installed. Finish a game before changing apps manually. Starting a registered game selects Buddy automatically; you do not need a browser open for game commands to reach him.

| Status | What it tells you |
| --- | --- |
| **GYROMITE / CONNECTED** | Mission is connected to the UNO Q with Gyromite selected. |
| **RETROPIE ONLINE** or **BATOCERA ONLINE** | Your console's receiver has checked in recently. |
| **GAME FRAMES LINKED** | Signals from the selected game are reaching Buddy. |

![Mission preview showing Buddy and the Gyromite accessories](images/mission-model-screenshot.png)

## Try a demonstration

When no supported game is running, select **Gyromite** or **Stack-Up** and **Run Demo Sequence**. Gyromite demonstrates a held unspun gyro, two spinning gyros on pads, spin-down, re-spin, and return to holders. The illustrative spin clock is 55 seconds. Stack-Up moves red alone and then a blue/white group. **Home** resets the pieces. Pose Lab is a character-only movement sandbox. A live game launch stops the demo and selects that game's scene.

## Choose an NES emulator

For automatic R.O.B. movement on RetroPie, select **lr-robvision-fceumm** or **lr-robvision-nestopia** for the game. These choices let the game send Buddy its commands. On supported Batocera, the installer selects the R.O.B. Vision FCEUmm wrapper for registered games; Nestopia is available as a per-game choice. See the [RetroPie](../deploy/retropie/README.md) and [Batocera](../deploy/batocera/README.md) setup guides.

## Play Gyromite

Open [Setup](../dashboard/setup.html) to check the console and game-frame status. Start Gyromite and watch Mission for **GAME FRAMES LINKED**. R.O.B. follows complete commands from the game. A spinning virtual gyro on a pad keeps its gate pressed while R.O.B. moves elsewhere; an unspun gyro can press one gate while held there. The matching gate on the game screen should move.

**Fast Gates** responds immediately while Gyromite is selected. Tap **Lower Blue** or **Lower Red** to press, tap again to release, or choose **Release Both**. On Mission, **2** toggles blue, **1** toggles red, and **0** releases both while you are not typing in a field. Holds expire after 60 seconds; both buttons release on game exit or lost receiver data. Buddy's hands must be empty, the matching gyro must be on its holder, and the target pad must be free. Return the pieces with regular controls or choose **Home** to reset the gyros. Watch the game screen to confirm the gate's response.

## Play Stack-Up

The live model begins with five colored blocks on Tray 3. In Direct mode, jumping Hector onto a command tile sends **Left, Right, Up, Down, Open,** or **Close** through the frame link. Manual controls use the same virtual model. A lower grip carries the contacted block and all blocks above it. Impossible moves are rejected and leave pieces in place. **Home** restores the initial stack.

## Current game limits

Stack-Up's virtual arrangement does not score a round or initialize Bingo's distinct starting layout. Use the game screen to check its target and result. Stack-Up does not use Gyromite's gate-button return path.

## Test mode and reset

Launch the game through its R.O.B. Vision emulator choice and enter Test mode. The game-frame link makes R.O.B.'s red light blink automatically on Mission and Setup when it recognizes the Test signal. A separate ready-light command makes the light steady briefly. Exiting Test mode returns the UNO Q matrix to the game's eyes. Neither signal moves R.O.B. **Preview Red Light** on Setup demonstrates the animation without claiming a game signal.

**Home** resets the selected virtual game. Live **Emergency Stop** clears the game selection; in the offline preview it cancels the script until reset. A browser reload restores the UNO Q's current snapshot. See [Setup](SETUP_GUIDE.md), [gameplay](GAMEPLAY_GUIDE.md), and [troubleshooting](TROUBLESHOOTING.md).
