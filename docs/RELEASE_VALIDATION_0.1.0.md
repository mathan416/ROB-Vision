# 0.1.0 release validation — 25 September 2026

RC7 is a prerelease. The final release gate has not passed.

## Published installation checks

- The public one-command RC4 UNO Q upgrade stopped and restarted its App Lab app, compiled and uploaded the matrix sketch, and served Mission, Setup, Help, the API, and the updated PDF manuals over port 80.
- The public one-command RC3 RetroPie upgrade completed on `retropie.local` with EmulationStation closed. After reboot, `rob-vision-controller2.service` was active with no restarts and EmulationStation was running. The earlier InputManager assertion was not seen in the remote process and service checks. The player's visual reboot check is still pending.
- The public RC4 through RC7 Batocera commands upgraded the supported 43.1 x86_64 host and resumed EmulationStation. Its receiver remained active and the UNO Q listed both consoles online. RC7 detected the virtual pad as RetroArch index 2; Linux assigned it `js4`.

## Games and input

- On Batocera, Gyromite and Stack-Up each launched with the FCEUmm and Nestopia wrappers. During each launch the UNO Q selected the exact game and reported a live frame link; exit cleared the session. Earlier live Direct-mode sessions decoded commands from both games.
- A temporary virtual keyboard entered Gyromite Game A on Batocera. Holding a temporary Player 2 keyboard binding moved the blue gates on screen. The production receiver emitted Linux button events 304 and 305 when the UNO Q's Gate Assist was pressed. RetroArch detected the virtual controller as pad 2, assigned Player 2 to a Gamepad, and loaded Batocera's common remap. Batocera initially generated pad 2 for both Player 1 and Player 2; isolating Player 1 on pad 0 did not establish a reliable blue response. A timing-matched run without pad input showed the blue gates stayed raised. Red-only holds lowered them, while blue-only holds did not, including with receiver button codes swapped. A trial direct libretro return path was not validated and was reverted. Temporary host settings and diagnostic code were restored after the tests.
- RetroPie's FCEUmm blue and red gates previously worked in Game A. Nestopia's Gyromite gate return still needs a live Game A check. Stack-Up Memory and Bingo remain outside the 0.1.0 gameplay claim.

## Automated checks

The Python suite, five JavaScript model tests, shell syntax, release checksum tests, and Git diff checks passed during candidate preparation. The repository and packages were scanned for tracked ROMs and known credential patterns. These checks do not replace the failed Batocera Game A return-path test.

**Release decision:** do not publish final `v0.1.0` until the Batocera gate path is fixed and both supported consoles pass the remaining gate checks.
