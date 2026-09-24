# Gyromite manual: design and test notes

**Source:** [Gyromite instruction booklet transcript](https://www.digitpress.com/library/manuals/nes/gyromite.txt) at Digital Press. This is a paraphrased summary of Nintendo's physical game accessory, translated into rules for a virtual R.O.B. The transcript includes editorial notes and possible transcription mistakes; confirm game behavior with a user-supplied game before claiming compatibility.

## Original accessory and virtual equivalent

The original set has one motorized spinner, two gyro holders, red/blue gyro trays, removable hands, and a holder for Controller 2. A gyro on the blue tray lowers the blue gate; one on red lowers the red gate. The original trays press Controller 2 mechanically. R.O.B. Vision draws these objects and derives a **virtual** red/blue button state in UNO Q software, then sends it over Wi-Fi or Ethernet to a paired virtual Controller 2 receiver. There are no physical gyros, trays, or contact sensors in this project. The transcript does not unambiguously map tray colors to Controller 2 A/B. On the RetroPie test setup, an isolated blue virtual pad press moved the blue Game A gate after its A/B mapping was corrected; the red gate awaits a safe visual check.

The booklet says that **one gate can be operated without spinning a gyro**. R.O.B. may hold an unspun gyro down on a pad, then lift it to release. When both gates need control, a spinning gyro remains upright on one pad while R.O.B.'s hands move the other. The original setup begins with both gyros in holders, and the instructions describe R.O.B. moving a gyro between holder, spinner, and tray. The virtual controller therefore treats holders as resting positions and the spinner as an optional step driven by game needs.

## Game modes

| Mode | Manual behavior | Virtual design implication |
| --- | --- | --- |
| Test | Optical aiming signal | Provide camera framing and decoder diagnostics before play. |
| Direct | Up/down/left/right/open/close go straight to R.O.B. | Validate six optical commands and show each virtual movement. |
| Game A | Player controls the professor on a dark screen; Start enters a blue robot-transmission screen | Decode complete robot commands in the correct mode; avoid claiming to know professor position from flashes. |
| Game B | Professor walks while Controller 1 commands R.O.B. directly | Show ready/busy state and virtual-pad-to-game latency. |

## Acceptance questions

- Capture Test and six Direct commands on the intended LCD/OLED and emulator.
- Demonstrate held unspun press/release of one virtual pad.
- Demonstrate two independent gyro positions and spin-down phases, red/blue button state, and return to holders.
- Measure red/blue-to-A/B mapping, receiver freshness, and actual game gate response. A local visual button state is not proof that the emulator accepted input.
- Test Game A's transmission switch and Game B's direct command cadence.

Original booklet warnings about touching real spinning gyros are historical context. The [virtual system contract](VIRTUAL_SYSTEM.md) is the current product scope.
