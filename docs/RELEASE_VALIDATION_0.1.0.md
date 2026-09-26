# 0.1.0 release validation — 25 September 2026

RC7 is a prerelease. The final release gate has not passed.

## Published installation checks

- The public one-command RC4 UNO Q upgrade stopped and restarted its App Lab app, compiled and uploaded the matrix sketch, and served Mission, Setup, Help, the API, and the updated PDF manuals over port 80.
- The public one-command RC3 RetroPie upgrade completed on `retropie.local` with EmulationStation closed. After reboot, `rob-vision-controller2.service` was active with no restarts and EmulationStation was running. The earlier InputManager assertion was not seen in the remote process and service checks. The player's visual reboot check is still pending.
- The public RC4 through RC7 Batocera commands upgraded the supported 43.1 x86_64 host and resumed EmulationStation. Its receiver remained active and the UNO Q listed both consoles online. RC7 detected the virtual pad as RetroArch index 2; Linux assigned it `js4`.

## Games and input

- On Batocera, Gyromite and Stack-Up each launched with the FCEUmm and Nestopia wrappers. During each launch the UNO Q selected the exact game and reported a live frame link; exit cleared the session. Earlier live Direct-mode sessions decoded commands from both games.
- Batocera's EmulationStation mapping identifies the physical Atari controller as SDL joystick 0. The R.O.B. Vision virtual pad is joystick 2. The installed per-ROM configuration now assigns Player 1 to 0 and Player 2 to 2, with both ports using A=0 and B=1; Buddy's receiver swaps its Linux button events to match those logical buttons. The Batocera-specific autoconfiguration profile also uses A=0 and B=1. A clean installer upgrade preserved pairing and resumed EmulationStation.
- Automated Gyromite Game A screenshots with the production FCEUmm path measured the visible blue gate at vertical pixels 209–428 before a blue press, 356–576 during the hold, and 209–428 after release. A red-only hold left the blue gate at 209–428. This confirmed the Player 2 gamepad and blue gate return on the tested Batocera host.
- The same physical and virtual pad assignments were generated for Nestopia. Batocera's bundled Nestopia did not visibly move the Game A blue gate. A temporary trace showed it did not request Player 2 input from RetroArch. The current official Libretro Nestopia build did request Player 2 and saw A and B holds, but the gate still did not move. An explicit NTSC adapter option and a post-ROM-load gamepad reconnection also failed the visual gate test. Those diagnostic binaries and options were restored; the Batocera game selection remains on the verified FCEUmm path. Nestopia's Gyromite gate return is unverified and blocks a release claim for that combination.
- RetroPie's FCEUmm blue and red gates previously worked in Game A. Nestopia's Gyromite gate return still needs a live Game A check. Stack-Up Memory and Bingo remain outside the 0.1.0 gameplay claim.

## Automated checks

The Python suite, five JavaScript model tests, shell syntax, release checksum tests, and Git diff checks passed during candidate preparation. The repository and packages were scanned for tracked ROMs and known credential patterns. These checks do not replace the failed Batocera Game A return-path test.

**Release decision:** do not publish final `v0.1.0` until the Batocera gate path is fixed and both supported consoles pass the remaining gate checks.
