# Gyromite manual: historical behavior and virtual rules

**Source:** [Gyromite instruction booklet transcript](https://www.digitpress.com/library/manuals/nes/gyromite.txt) at Digital Press. This paraphrases the original accessory rules and relates them to R.O.B. Vision. The transcript may contain transcription mistakes; the [verification plan](VERIFICATION_PLAN.md) records checks against the running game.

## Original accessory and virtual equivalent

The original set has one motorized spinner, two gyro holders, red/blue gyro trays, removable hands, and a holder for Controller 2. A gyro on the blue tray lowers the blue gate; one on red lowers the red gate. The original trays press Controller 2 mechanically. R.O.B. Vision draws these objects and derives a **virtual** red/blue button state in UNO Q software, then sends it over Wi-Fi or Ethernet to a paired virtual Controller 2 receiver. The transcript does not unambiguously map tray colors to Controller 2 A/B. On the RetroPie test setup, an isolated blue virtual pad press moved the blue Game A gate after its A/B mapping was corrected; the player later confirmed that both red and blue controls work.

The booklet says that **one gate can be operated without spinning a gyro**. R.O.B. may hold an unspun gyro down on a pad, then lift it to release. When both gates need control, a spinning gyro remains upright on one pad while R.O.B.'s hands move the other. The original setup begins with both gyros in holders, and the instructions describe R.O.B. moving a gyro between holder, spinner, and tray. The virtual controller therefore treats holders as resting positions and the spinner as an optional step driven by game needs.

## Game modes

| Mode | Manual behavior | R.O.B. Vision behavior |
| --- | --- | --- |
| Test | Optical aiming signal | Blink the virtual red head light while the linked game sends its Test signal. |
| Direct | Up/down/left/right/open/close go straight to R.O.B. | Apply each complete game-frame command as one virtual movement. |
| Game A | Player controls the professor on a dark screen; Start enters a blue robot-transmission screen | Apply complete robot commands; the game screen shows the professor's position. |
| Game B | Professor walks while Controller 1 commands R.O.B. directly | Apply complete robot commands and return virtual pad states to Controller 2. |

The [verification plan](VERIFICATION_PLAN.md) tracks game-mode and Controller 2 checks. The [virtual system contract](VIRTUAL_SYSTEM.md) describes the current product behavior.
