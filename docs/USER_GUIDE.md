# R.O.B. Vision user guide

The UNO Q controls Buddy, the virtual robot shown in Mission. RetroPie or Batocera sends Gyromite and Stack-Up commands through the game-frame link. His movements and game pieces appear in your browser.

## Open R.O.B. Vision

Install version 0.1.6 with the two commands in the [installation guide](INSTALLATION_GUIDE.md): one on the UNO Q, one on the console. The console command prints first-time pairing details for Setup and configures its receiver automatically.

Start **R.O.B. Vision** in UNO Q App Lab, then open one of the Mission URLs printed by the installer on a laptop, phone, or tablet. The installer prints both the UNO Q's `.local` hostname and its LAN IP address. Stop another App Lab app first if one is running. A `file://` page is an offline preview.

Mission shows R.O.B., Accessory Bay, Game Table, Pose Preview, System Vitals, and Activity Feed. **GYROMITE / CONNECTED** means the browser reaches the UNO Q with Gyromite selected. **RETROPIE ONLINE** or **BATOCERA ONLINE** means that console's receiver has contacted the UNO Q recently. **GAME FRAMES LINKED** means the selected game is sending its rendered frames.

![Mission preview showing Buddy and the Gyromite accessories](images/mission-model-screenshot.png)

## Try a demonstration

When no supported game is running, select **Gyromite** or **Stack-Up** and **Run Demo Sequence**. Gyromite demonstrates a held unspun gyro, two spinning gyros on pads, spin-down, re-spin, and return to holders. The illustrative spin clock is 55 seconds. Stack-Up moves red alone and then a blue/white group. **Home** resets the pieces. Pose Lab is a character-only movement sandbox. A live game launch stops the demo and selects that game's scene.

## Choose an NES emulator

For automatic R.O.B. movement on RetroPie, select **lr-robvision-fceumm** or **lr-robvision-nestopia** for the game. Each entry uses the corresponding installed core and forwards the game's rendered light cells to the UNO Q. On supported Batocera, the installer selects the R.O.B. Vision FCEUmm wrapper for registered games; Nestopia is available as a per-game choice. See the [RetroPie](../deploy/retropie/README.md) and [Batocera](../deploy/batocera/README.md) setup guides.

## Play Gyromite

Open [Setup](../dashboard/setup.html) to check the console and game-frame status. Start Gyromite and watch Mission for **GAME FRAMES LINKED**. R.O.B. follows complete commands from the game. A spinning virtual gyro on a pad keeps its gate pressed while R.O.B. moves elsewhere; an unspun gyro can press one gate while held there. The UNO Q sends those pad states to the active console's virtual Controller 2.

**Fast Gates** responds immediately while Gyromite is selected. Tap **Lower Blue** or **Lower Red** to press, tap again to release, or choose **Release Both**. Keyboard shortcuts are **2**, **1**, and **0**. Holds expire after 60 seconds; both buttons release on game exit or lost receiver data. If regular controls moved a gyro, use **Home** to restore its holder before Fast Gates. Watch the game screen to confirm the gate's response.

## Play Stack-Up

The live model begins with five colored blocks on Tray 3. In Direct mode, jumping Hector onto a command tile sends **Left, Right, Up, Down, Open,** or **Close** through the frame link. Manual controls use the same virtual model. A lower grip carries the contacted block and all blocks above it. Impossible moves are rejected and leave pieces in place. **Home** restores the initial stack.

## Current game limits

Stack-Up's virtual arrangement does not score a round or initialize Bingo's distinct starting layout. Use the game screen to check its target and result. Stack-Up does not use Gyromite's gate-button return path.

## Test mode and reset

Launch the game through its R.O.B. Vision emulator choice and enter Test mode. The game-frame link makes R.O.B.'s red light blink automatically on Mission and Setup when it recognizes the Test signal. A separate ready-light command makes the light steady briefly. Exiting Test mode returns the UNO Q matrix to the game's eyes. Neither signal moves R.O.B. **Preview Red Light** on Setup demonstrates the animation without claiming a game signal.

**Home** resets the selected virtual game. Live **Emergency Stop** clears the game selection; in the offline preview it cancels the script until reset. A browser reload restores the UNO Q's current snapshot. See [Setup](SETUP_GUIDE.md), [gameplay](GAMEPLAY_GUIDE.md), and [troubleshooting](TROUBLESHOOTING.md).
