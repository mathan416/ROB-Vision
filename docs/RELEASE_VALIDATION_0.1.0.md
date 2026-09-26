# 0.1.0 release validation — 25 September 2026

RC6 is a prerelease. The final release gate has not passed.

## Published installation checks

- The public one-command RC4 UNO Q upgrade stopped and restarted its App Lab app, compiled and uploaded the matrix sketch, and served Mission, Setup, Help, the API, and the updated PDF manuals over port 80.
- The public one-command RC3 RetroPie upgrade completed on `retropie.local` with EmulationStation closed. After reboot, `rob-vision-controller2.service` was active with no restarts and EmulationStation was running. The earlier InputManager assertion was not seen in the remote process and service checks. The player's visual reboot check is still pending.
- The public RC4, RC5, and RC6 Batocera commands upgraded the supported 43.1 x86_64 host and resumed EmulationStation. Its receiver remained active and the UNO Q listed both consoles online. RC6 detected the virtual pad as RetroArch index 2; Linux assigned it `js4`.

## Games and input

- On Batocera, Gyromite and Stack-Up each launched with the FCEUmm and Nestopia wrappers. During each launch the UNO Q selected the exact game and reported a live frame link; exit cleared the session. Earlier live Direct-mode sessions decoded commands from both games.
- A temporary virtual keyboard entered Gyromite Game A on Batocera. Holding a temporary Player 2 keyboard binding moved the blue gates on screen. The production virtual controller emitted its blue and red Linux button events when the UNO Q's Gate Assist was pressed, but the Game A gate did not visibly move in repeated FCEUmm captures. Changing the Player 2 joystick index from Linux `js4` to RetroArch pad 2, adding the udev controller profile, and reversing A/B assignments individually did not establish a visible gate response. Temporary keyboard bindings and A/B changes were restored after each diagnostic run.
- RetroPie's FCEUmm blue and red gates previously worked in Game A. Nestopia's Gyromite gate return still needs a live Game A check. Stack-Up Memory and Bingo remain outside the 0.1.0 gameplay claim.

## Automated checks

The Python suite, five JavaScript model tests, shell syntax, release checksum tests, and Git diff checks passed during candidate preparation. The repository and packages were scanned for tracked ROMs and known credential patterns. These checks do not replace the failed Batocera Game A return-path test.

**Release decision:** do not publish final `v0.1.0` until the Batocera gate path is fixed and both supported consoles pass the remaining gate checks.
