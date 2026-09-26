# R.O.B. Vision UNO Q hardware setup

The setup consists of an Arduino UNO Q, a supported RetroPie or Batocera game host, a network connection, and a browser display for Buddy and his accessories.

| Item | Role |
| --- | --- |
| Arduino UNO Q | Runs the App Lab controller, virtual game state, HTTP panel, and LED matrix sketch. |
| RetroPie or supported Batocera host | Runs Gyromite or Stack-Up, sends verified game-frame commands, and receives Gyromite's virtual Controller 2 state. |
| UNO Q power and optional enclosure | Provide a suitable supply and ventilation. |
| Wi-Fi or Ethernet adapter | Connects the UNO Q and game host on the same trusted LAN. An Ethernet adapter can use a USB hub. |
| Laptop, tablet, or phone | Displays Buddy and the virtual game accessories in a browser. |

Power the UNO Q with a suitable supply and keep its vents clear. Open `http://<your-uno-hostname>.local/dashboard/` or `http://<your-uno-ip-address>/dashboard/` on a laptop, iPad, or phone. The UNO Q's 13×8 LED matrix provides small status animations.

Install the console integration with the [release command](INSTALLATION_GUIDE.md). RetroPie provides R.O.B. Vision FCEUmm and Nestopia launch choices; supported Batocera selects the FCEUmm wrapper for registered ROMs and offers Nestopia as a per-game choice. Start either registered game and verify **GAME FRAMES LINKED** on Mission.
