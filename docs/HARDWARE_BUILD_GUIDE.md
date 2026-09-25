# R.O.B. Vision UNO Q hardware setup

R.O.B. and every accessory are virtual. The physical build consists of an Arduino UNO Q, a RetroPie game host, network connection, and a browser display. No robot mechanism, accessory sensor, or camera is needed.

Power the UNO Q with a suitable supply and keep its vents clear. The tested setup uses Ethernet through a USB hub; Wi-Fi carries the same traffic. Open `http://arduiain.local/dashboard/` on a laptop, iPad, or phone. The UNO Q's 13×8 LED matrix provides small status animations.

On RetroPie, install the launch hooks, paired Controller 2 receiver, and R.O.B. Vision FCEUmm or Nestopia frame-link choice. Start either registered game and verify **GAME FRAMES LINKED** on Mission. Both Gyromite gate colors were confirmed in Game A. Check Test mode and each movement command with the [verification plan](VERIFICATION_PLAN.md).

See [installation](INSTALLATION_GUIDE.md) for deployment steps.
