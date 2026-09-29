# R.O.B. Vision quick reference

The UNO Q controls Buddy's movement and game pieces. RetroPie or supported Batocera sends game signals to the UNO Q.

| Where | Action | Result |
| --- | --- | --- |
| Mission | Select Gyromite, Stack-Up, or Pose Lab | Choose the virtual scene while no game is active. |
| Mission | Run Demo Sequence | Finite animation; available while paired and idle. |
| Mission | Home | Reset selected virtual game and pieces. |
| Mission | Emergency Stop | Live: clear game and release pads. Preview: cancel local script. |
| Mission | Fast Gates during live Gyromite | Blue `2`, red `1`, Release Both `0`; press again to release a color. Auto-release after 60 seconds. |
| Setup | Pair Console / Check Link | Pair a console or refresh its authenticated online status. |
| Game Test mode | Automatic red light | Blink R.O.B.'s red light when linked game frames carry the Test signal; no movement. |
| Setup | Gyromite / Stack-Up checks | Send manual pad or movement commands to the live model. |
| Mission | GAME FRAMES LINKED | The console is sending game signals for the selected ROM; automatic movement uses those frames. |

In Stack-Up, press Select on the ROBOT BLOCK screen, choose Test, then press Start. The artwork remains visible while the Test signal plays.

Open your UNO Q address to visit Buddy, or choose R.O.B. Vision if both apps are installed. The installer also prints direct Mission and Setup links using the device name and IP address.

If a move is blocked, read the Activity Feed, raise Buddy's hands if needed, and try again. For controls and game pieces, see the [Game Manual](GAME_MANUAL.md). For a connection problem, see [Troubleshooting](TROUBLESHOOTING.md).
