# R.O.B. Vision gameplay guide

The UNO Q updates Buddy and the game pieces shown in your browser. A paired RetroPie or supported Batocera console sends movement commands from the game; Gyromite's virtual pad states return to that console's Controller 2.

## Gyromite

The [original Gyromite booklet](https://www.digitpress.com/library/manuals/nes/gyromite.txt) describes **Test**, **Direct**, **Game A**, and **Game B**. Direct sends six R.O.B. actions: up, down, left, right, open, and close. In Game A, Start switches into the robot-transmission screen for a command and then back to the professor. In Game B, the professor walks while Controller 1 directly commands R.O.B. A gyro on the blue or red tray lowers the matching gate.

The manual explicitly says a gyro **does not need to spin to operate only one gate**. R.O.B. can hold an unspun gyro on the virtual pad, then lift it to release that pad. If both gates must be controlled, spinning one gyro lets it stay upright on one pad while R.O.B. uses his hands to put the other on the other pad. A gyro that is no longer needed belongs on its holder. The spinner is a means to free R.O.B.'s hands, not an obligatory step for every pad press.

**Try the demo:** with no game running, select Gyromite and **Run Demo Sequence**. Buddy presses a pad with an unspun gyro, uses two spinning gyros, and returns them to their holders. The sequence stops at `COMPLETE`. Select **Home** to reset. The demo's spin lifetime is illustrative.

**During play:** the UNO Q tracks both gyros and sends red and blue pad states to the active console. It releases both buttons on game exit or a lost link. **Fast Gates** presses or releases a matching pad immediately; each hold expires after 60 seconds. Watch the game screen for Hector and the gate response.

![Mission preview controls and Gyromite Game Table](images/mission-controls-screenshot.png)

*Pose Preview, Game Table, and System Vitals. Fast Gates appears during live Gyromite play.*

## Stack-Up

The [Stack-Up booklet](https://www.digitpress.com/library/manuals/nes/Stack-up.pdf) describes Direct, Memory, and Bingo. Buddy's Game Table has five trays and five colored blocks. Direct and Memory start with all five on Tray 3, top to bottom **red, white, blue, yellow, green**. In Direct mode, move Professor Hector onto the **left, right, up, down, open,** or **close** command keys. Memory plays a programmed command series; Bingo sends a command when one row or column completes. Buddy can carry a block with all the blocks above it.

**Try the demo:** with no game running, select Stack-Up and **Run Demo Sequence**. Buddy moves red alone, then carries blue and white together. All five blocks remain visible in the Live Model, Accessory Bay, and Game Table. The **Stack-Up Commands** buttons apply one virtual action at a time. **Home** restores the starting stack. If a move is blocked, the pieces stay in place and the Activity Feed explains why.

**Current limits:** Buddy starts with the Direct/Memory stack in every Stack-Up mode; Bingo's different starting arrangements are not modeled. Compare the virtual arrangement with the game's target on its screen. The game sends movement commands but does not tell Buddy its target, score, or whether the round was completed. Stack-Up does not use Gyromite's gate-button return path.

## Pose Lab and recovery

Pose Lab lets you try Buddy's head, body turn, arms, and shared grip. Its short demo is a greeting. If the browser reconnects during a game, it resumes from the UNO Q's current state. If the Gyromite link drops, both virtual gate buttons release.
