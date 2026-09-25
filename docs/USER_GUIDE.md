# R.O.B. Vision user guide

**Current release:** The UNO Q hosts a live virtual R.O.B. dashboard and RetroPie link. Both Gyromite gate controls have been confirmed in Game A. A real camera and display have not yet passed optical-command testing. R.O.B., gyros, blocks, trays, and spinner are graphics and software state, not physical objects.

## Open R.O.B. Vision

Start **R.O.B. Vision** in UNO Q App Lab, then open `http://arduiain.local/dashboard/` on a laptop, phone, or tablet. App Lab runs one app at a time on this UNO Q; stop VirtualGlove before starting R.O.B. Vision. The direct `http://arduiain.local:8766/dashboard/` address reaches the same controller. A page opened from `file://` is an offline preview and does not show live RetroPie state.

Mission keeps the animated R.O.B. as the main view. Accessory Bay and Game Table show his virtual game pieces. Pose Preview and System Vitals sit beside the Game Table; the Activity Feed reports controller actions. A label such as **GYROMITE / CONNECTED** means Gyromite is selected and this browser can reach the UNO Q. RetroPie status appears separately as **RETROPIE ONLINE** or **RETROPIE OFFLINE**; neither label proves the camera is reading valid commands.

![Live Mission page showing R.O.B., the active Gyromite scene, and accessories](images/mission-model-screenshot.png)

*Mission on the UNO Q, with Gyromite selected. The camera was not attached when this screenshot was taken.*

## Try the demonstration

When no supported game is running, select **Gyromite** or **Stack-Up** and **Run Demo Sequence**. It works even if RetroPie is paired but idle. Gyromite demonstrates a held unspun gyro, two spinning gyros on pads, spin-down, re-spin, and return to holders. The illustrative spin clock is 55 seconds. Stack-Up moves red alone and then a blue/white group. **Home** resets the pieces. Pose Lab is a character-only movement sandbox. A live game launch stops the demo and selects that game's scene.

## Play Gyromite

Open [Setup](../dashboard/setup.html) to check the RetroPie link and, when a camera is attached, frame the game display. On Mission, **Fast Gates** works while Gyromite is selected and camera capture is stopped. Tap **Lower Blue** or **Lower Red** to press immediately, tap again to release, or select **Release Both**. Keyboard shortcuts are **2**, **1**, and **0**. Presses expire after 60 seconds. Both buttons release on game exit or lost receiver data. If you moved a gyro with normal controls, select **Home** before Fast Gates to restore their holders.

A spinning virtual gyro on a pad keeps its gate pressed while R.O.B. moves elsewhere. An unspun gyro can press one gate while R.O.B. holds it there. The UNO Q sends the resulting pad states to RetroPie's virtual Controller 2. The player confirmed red and blue gate responses with the current mapping. The game screen itself remains the authority for Hector's position and gate animation.

## Play Stack-Up

Stack-Up starts with all five colored blocks on Tray 3 in the current live model. Manual **Left, Right, Up, Down, Open, Close** actions move the arm and ordered block groups. A lower grip carries the contacted block and all those above it. Impossible moves are rejected and leave the blocks in place. The model does not currently initialize the distinct historical Bingo starting layout or judge a game's score. Stack-Up has no Gyromite-style Controller 2 gate path.

## Camera and reset

On Setup, **Start Camera Check** shows the camera image, sampling rectangle, signal, and measured frame rate. **Watch Test Flashes** blinks the virtual red light when sustained Test-mode alternation is recognized; it does not move R.O.B. **Reset & Reconnect** closes and retries the camera in software. This does not power-cycle the USB hub. The camera capture code requests 60 fps, but real optical play still needs validation with the intended camera and game display.

**Home** resets the selected virtual game. Live **Emergency Stop** stops camera capture and clears the game selection; in the offline preview it cancels the scripted animation until reset. A browser reload restores the UNO Q's current snapshot. See [Setup](SETUP_GUIDE.md), [gameplay](GAMEPLAY_GUIDE.md), and [troubleshooting](TROUBLESHOOTING.md).
