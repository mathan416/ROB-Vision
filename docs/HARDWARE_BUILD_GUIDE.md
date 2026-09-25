# R.O.B. Vision UNO Q hardware setup

R.O.B., hands, gyros, spinner, pads, and Stack-Up blocks are virtual. The existing UNO Q App Lab app, matrix sketch, browser dashboard, and RetroPie link are running. The remaining physical work is a compatible camera, stable aim at the game display, and optional mounting/enclosure. No motors, mechanical robot, or accessory sensors are needed.

Use a suitable UNO Q power supply and keep its vents clear. The tested setup uses an Ethernet adapter attached through a USB hub. Wi-Fi can carry the same controller traffic. A laptop, iPad, or phone is the main R.O.B. display at `http://arduiain.local/dashboard/`. The built-in 13×8 LED matrix supplies small status animations, not the game table.

Before buying or fixing the camera mount, identify the actual UNO Q capture device and measure delivered 30/60 fps modes, focus, exposure, and flash sampling on the intended LCD/OLED. The current code excludes codec-only `/dev/video` nodes. A camera was not attached during the engineering tests; the setup page's reconnect action retries software capture only. The optional USB recovery host helper is supplied but not installed and avoids a whole-hub reset when Ethernet shares the hub.

The RetroPie Controller 2 mapping and both Gyromite gate colors have already been verified. Commission remaining hardware in this order: attach and aim camera, observe both games' Test modes, collect repeated complete movement traces and idle false-trigger evidence, then run full interactive Gyromite and Stack-Up sessions. See [installation](INSTALLATION_GUIDE.md) and [verification](VERIFICATION_PLAN.md).
