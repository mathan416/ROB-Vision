# R.O.B. Vision quick reference

**R.O.B. is virtual.** The UNO Q app and RetroPie link are running. Both Gyromite gate colors responded in Game A. The camera recognized both games' Test modes. RetroPie's game-frame link sent all six commands from each game to the virtual R.O.B. during live Direct play.

| Where | Action | Result |
| --- | --- | --- |
| Mission | Select Gyromite, Stack-Up, or Pose Lab | Choose the virtual scene while no game is active. |
| Mission | Run Demo Sequence | Finite animation; available while paired and idle. |
| Mission | Home | Reset selected virtual game and pieces. |
| Mission | Emergency Stop | Live: stop capture and clear game. Preview: cancel local script. |
| Mission | Fast Gates during live Gyromite | Blue `2`, red `1`, Release Both `0`; press again to release a color. Auto-release after 60 seconds. |
| Setup | Pair Console / Check Link | Pair RetroPie or refresh its authenticated online status. |
| Setup | Start Camera Check | Show framing, measured fps, and sampling rectangle. |
| Setup | Reset & Reconnect | Retry OpenCV capture; USB hub is unaffected. |
| Setup | Watch Test Signal | Blink R.O.B.'s red light for a detected Test signal; no movement. |
| Setup | Gyromite / Stack-Up checks | Send manual pad or movement commands to the live model. |
| Mission | GAME FRAMES LINKED | RetroPie is sending rendered game frames for the selected ROM; automatic movement does not require the camera. |

In Stack-Up, press Select on the ROBOT BLOCK screen, choose Test, then press Start. The artwork remains visible while the Test signal plays.

Use [Mission](http://arduiain.local/dashboard/) and [Setup](http://arduiain.local/dashboard/setup.html) on the UNO Q. A local `file://` page is only the preview. The camera requests 60 fps for preview and Test checks; the RetroPie frame link reads complete commands at the game's own frame rate.

The game launch hook identifies an exact ROM name. The receiver applies Gyromite virtual pad states as Controller 2 input and releases both on exit or stale network data. Stack-Up moves modeled blocks and has no gate-button return path. See the [user guide](USER_GUIDE.md) and [troubleshooting](TROUBLESHOOTING.md).
