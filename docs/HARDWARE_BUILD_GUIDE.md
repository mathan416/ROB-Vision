# R.O.B. Vision UNO Q hardware setup

R.O.B., hands, gyros, spinner, pads, and Stack-Up blocks are virtual. The existing UNO Q App Lab app, matrix sketch, browser dashboard, and RetroPie link are running. The remaining physical work is a compatible camera, stable aim at the game display, and optional mounting/enclosure. No motors, mechanical robot, or accessory sensors are needed.

Use a suitable UNO Q power supply and keep its vents clear. The tested setup uses an Ethernet adapter attached through a USB hub. Wi-Fi can carry the same controller traffic. A laptop, iPad, or phone is the main R.O.B. display at `http://arduiain.local/dashboard/`. The built-in 13×8 LED matrix supplies small status animations, not the game table.

The attached Razer Kiyo Pro is identified as `/dev/video2` and reaches about 60 delivered fps at 640×480 MJPEG with its temporary HDR-off and fixed-rate exposure setting. Keep the camera aimed so Setup's green rectangle surrounds the game's optical area, then validate flash sampling on the intended LCD/OLED before fixing the mount. The code excludes codec-only `/dev/video` nodes. Setup's reconnect action retries software capture only. The optional USB recovery host helper is supplied but not installed and avoids a whole-hub reset when Ethernet shares the hub.

The RetroPie Controller 2 mapping and both Gyromite gate colors have already been verified. Commission remaining hardware in this order: attach and aim camera, observe both games' Test modes, collect repeated complete movement traces and idle false-trigger evidence, then run full interactive Gyromite and Stack-Up sessions. See [installation](INSTALLATION_GUIDE.md) and [verification](VERIFICATION_PLAN.md).
