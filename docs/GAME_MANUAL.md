# Play Gyromite and Stack-Up with Buddy

The UNO Q receives complete movement commands from a supported game's game signals. Buddy acts on those commands in the browser; the game continues on your console screen. Keep Mission open on a laptop, tablet, or phone to see Buddy, the accessories, and the Game Table. The console game remains the source for Hector's position, goals, and score.

## Before you play

Pair your console in Setup, then launch an exact registered Gyromite or Stack-Up ROM through a R.O.B. Vision core. Mission and Setup should show **GAME FRAMES LINKED**. When a game enters Test mode, Buddy's red light blinks and the UNO Q matrix shows **T**; Test is a link check, not a movement. A ready-light command gives a brief steady red light.

With no supported game active, choose a game on Mission and run its finite **Demo Sequence**. The demo also works while a console is paired but idle. Choose **Home** to restore the starting pose and pieces. During live play, Buddy follows the game's commands; the manual controls are useful for checks and recovery.

## Gyromite: two gates and two gyros

Gyromite gives Buddy two gyros, two holders, one spinner, and red and blue pads. A gyro pressing a coloured pad lowers the matching gate through the console's virtual Controller 2. Buddy can hold an **unspun** gyro on one pad, then lift it to release that gate. A **spinning** gyro can remain upright on one pad while Buddy moves the second gyro to the other. He returns a gyro to its holder when it is no longer needed. Spin duration in the virtual model is illustrative.

### Pick up and carry a gyro

1. Move Buddy to the gyro's holder.
2. From **Home** at level 6, send **Down** twice: first to level 4, then level 2.
3. Send **Close** to grasp the gyro between his hands.
4. Send **Up** once to level 4 before moving left or right.
5. Move to the spinner or coloured pad, then lower to level 2.

Both holders, the spinner, and the pads use level 2. Their different positions on screen come from the table's perspective. A held, unspun gyro can press one pad; lift it to release the gate. Spin a gyro when you want to leave it upright and free Buddy's hands.

| Mode | What to expect |
| --- | --- |
| Test | The game's Test signal blinks Buddy's red light. It does not move him. |
| Direct | Complete Up, Down, Left, Right, Open, and Close words move Buddy directly. |
| Game A | You control Hector; Start switches to the robot-transmission screen for a command and then back. The game screen shows Hector and the gates. |
| Game B | Hector walks while Controller 1 commands Buddy. Virtual pad states still return through Controller 2. |

**Fast Gates** gives an immediate check during live Gyromite: choose **Lower Blue** or **Lower Red** to press that pad, choose it again to release, or choose **Release Both**. On Mission, keyboard shortcuts are `2` to toggle blue, `1` to toggle red, and `0` to release both, provided you are not typing in a field. A hold expires after 60 seconds. Buddy's hands must be empty, the matching gyro must be on its holder, and the target pad must be free. Return the pieces with regular controls or choose **Home** to reset the gyros. On game exit or lost link, both pad states release.

![Mission controls and Gyromite Game Table](images/mission-controls-screenshot.png)

## Stack-Up: five trays and five blocks

Stack-Up has five coloured blocks and five trays around Buddy. Direct and Memory begin with every block on **Tray 3**, top to bottom: **red, white, blue, yellow, green**. Buddy's station can move among the trays, and his hands can move among six height levels. Closing on a lower block can pick up that block and every block above it as one ordered group. Opening places the group without changing its colour order.

In Direct mode, guide Hector onto the game's **Left, Right, Up, Down, Open,** or **Close** key. Each command moves Buddy once. The Game Piece card highlights the block Buddy can pick up or the group he carries. Watch the Live Model and Game Table as he moves. To move sideways past a stack, raise Buddy's hands above its top block first. Open hands can lower around the current stack to select a lower block; closed hands cannot lower into it. A blocked move leaves Buddy and every block in place, and the Activity Feed explains what to do. Play continues with the next command; **Home** restores the starting arrangement when you want a reset.

Memory sends a programmed command series; Bingo sends a command when a row or column is completed. Buddy follows the movement words, but the current model starts with the Direct/Memory Tray 3 stack in every mode. Bingo's different starting arrangements are not modeled. The game does not transmit a block colour, target tray, target arrangement, score, or round result. Compare the virtual arrangement with the target on your console screen. Stack-Up has no Gyromite gate-button return path.

![Stack-Up Game Table with five trays and all five blocks stacked on Tray 3](images/stack-up-game-table.png)

*Illustration of the current Game Table's starting arrangement. The block order and tray positions come from the dashboard model.*

## Recover and keep playing

If Mission reconnects during play, it resumes the UNO Q's current state. **Home** restores the selected game's virtual starting pose and pieces. **Emergency Stop** clears a live selection or cancels an offline preview animation. In Gyromite, release both Fast Gates before resetting. For a missing action, check **GAME FRAMES LINKED** and the Activity Feed; a command can be decoded correctly yet blocked by the virtual model's position or grip rule.
