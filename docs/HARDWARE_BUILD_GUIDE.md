# R.O.B. Vision UNO Q hardware setup

The setup consists of an Arduino UNO Q, a supported RetroPie or Batocera game host, a network connection, and a browser display for Buddy and his accessories.

Power the UNO Q with a suitable supply and keep its vents clear. The tested setup uses Ethernet through a USB hub; Wi-Fi carries the same traffic. Open `http://arduiain.local/dashboard/` on a laptop, iPad, or phone. The UNO Q's 13×8 LED matrix provides small status animations.

Install the console integration with the [release command](INSTALLATION_GUIDE.md). RetroPie provides R.O.B. Vision FCEUmm and Nestopia launch choices; supported Batocera selects the FCEUmm wrapper for registered ROMs and offers Nestopia as a per-game choice. Start either registered game and verify **GAME FRAMES LINKED** on Mission. Check Test mode and each movement command with the [verification plan](VERIFICATION_PLAN.md).

See [installation](INSTALLATION_GUIDE.md) for deployment steps.
