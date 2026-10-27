# Get back to playing with Buddy

Start with the symptom you can see. Try one check, then test the game again.

## The website will not open

1. Open your UNO Q's `.local` address on the same network.
2. If the name does not work, try the LAN IP link printed by its installer.
3. Choose R.O.B. Vision if the Apps page offers both controllers.

If neither address works, check the UNO Q's power and network connection. If an installation failed, keep its printed error and rerun the same installation command after fixing the reported problem.

## The console says Receiver Waiting

1. Turn on the console and check that it is connected to the same network.
2. In R.O.B. Vision Setup, choose **Check Link** beside that console.
3. Confirm the console is paired with this UNO Q.

A console connects to one UNO Q at a time. If you paired it with another, use that UNO Q or pair it here again. **Receiver Waiting** means there has been no recent receiver check-in; it does not prove the console is off.

## The game is running but Buddy does not move

1. Check that Setup shows the right game.
2. Look for **GAME FRAMES LINKED**.
3. On RetroPie, confirm the game uses **lr-robvision-fceumm** or **lr-robvision-nestopia**. On Batocera or Recalbox, launch the registered ROM; its per-game selection should use a R.O.B. Vision core.
4. Send one command in the game's **Direct** mode.
5. Read Mission's **Activity Feed**.

A blocked command can mean Buddy needs to raise his hands or move to the correct holder or tray. Follow the message and try again. If no game is selected, check its filename with **Edit ROMs** in Setup, then relaunch.

## Gyromite's gate does not move

1. Enter **Game A** and leave the matching coloured gate visible.
2. In Setup, choose **Lower Blue** or **Lower Red**.
3. Watch the game screen, then choose **Release Both**.
4. If it stays still, exit the game and open Router **Setup > Players**. Check your physical pad is Player 1 and Buddy is Player 2.
5. Under **Systems**, check NES uses **Controller Router**, then relaunch.

If Fast Gates reports that a piece is busy, return it with the normal controls or choose **Home** to reset the gyros. Fast Gates appears on Mission only during live Gyromite play.

## A gate stays down

Choose **Release Both**. Fast Gates also releases after 60 seconds. A gyro resting on a pad can keep the gate pressed during normal play; lift that gyro to release it.

## A Stack-Up move is blocked

Read the **Activity Feed**. Raise Buddy's hands above the destination stack before moving sideways. Open hands can lower around the current stack to select a block; closed hands cannot lower into it.

A blocked command leaves the blocks intact. Raise the hands and try again. Choose **Home** only when you want to restore the starting stack.

## My gamepad works in the menu but not in the game

Try another connected pad first: the one you are holding may be Player 2. Exit the game and check the named pads in Router **Setup > Players**. Choose **Test inputs**, press a button, then correct the assignment if needed. Save and relaunch.

If one game still picks the wrong player, check whether you saved different controller choices in that game's RetroArch settings. Those can take priority over Router. Keep unrelated game settings. The [Technical Reference](TECHNICAL_ARCHITECTURE.md#session-routing-across-retroarch-versions) explains how these settings interact.

## A wireless pad fell asleep or woke during play

Wake or reconnect it. Router keeps its player controllers connected and returns your pad to its saved player. If the Router service itself restarted, exit the game and relaunch once it is ready.

## Test mode does not blink the red light

Check the correct game and **GAME FRAMES LINKED**, then enter the game's **Test** mode. **Preview Red Light** only demonstrates the animation; it does not test the game connection.

## The demo will not start

Exit the running game first. Demos work while the console is paired and idle. Choose Gyromite or Stack-Up on Mission, then **Run Demo Sequence**. **Home** restores the starting pieces.

## RetroPie's game menu crashed during installation

Return to the console terminal and rerun the installer with EmulationStation closed. Keep it closed until installation finishes, then reopen it.

## Ask for help

Include the game, console platform, emulator choice, visible status, and the Activity Feed message. Describe what you tried and what happened. Keep pairing codes, tokens, private backups, and ROM files out of your report.
