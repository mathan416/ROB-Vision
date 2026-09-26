# R.O.B. Vision quick reference

The UNO Q controls Buddy's movement and game pieces. RetroPie or supported Batocera sends rendered game frames to the UNO Q.

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
| Mission | GAME FRAMES LINKED | The console is sending rendered game frames for the selected ROM; automatic movement uses those frames. |

In Stack-Up, press Select on the ROBOT BLOCK screen, choose Test, then press Start. The artwork remains visible while the Test signal plays.

Use the UNO Q installer's device-specific Mission and Setup links. Both `http://<hostname>.local/dashboard/` and `http://<LAN-IP>/dashboard/` open Mission; append `setup.html` for Setup. A local `file://` page is only the preview. The console frame link reads complete commands and Test signals at the game's own frame rate.

The game launch hook identifies an exact ROM name. The receiver applies Gyromite virtual pad states as Controller 2 input and releases both on exit or stale network data. Stack-Up moves modeled blocks and has no gate-button return path. See the [user guide](USER_GUIDE.md) and [troubleshooting](TROUBLESHOOTING.md).
