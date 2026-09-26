# 0.1.0 release validation — 26 September 2026

RC8 is a public prerelease. The final release gate has not passed because Batocera did not return to the network after its reboot check.

## Published installation checks

- The public one-command RC4 UNO Q upgrade stopped and restarted its App Lab app, compiled and uploaded the matrix sketch, and served Mission, Setup, Help, the API, and the updated PDF manuals over port 80.
- The public one-command RC3 RetroPie upgrade completed on `retropie.local` with EmulationStation closed. After reboot, `rob-vision-controller2.service` was active with no restarts and EmulationStation was running. The earlier InputManager assertion was not seen in the remote process and service checks. The player's visual reboot check is still pending.
- The public RC4 through RC7 Batocera commands upgraded the supported 43.1 x86_64 host and resumed EmulationStation. Its receiver remained active and the UNO Q listed both consoles online. RC7 detected the virtual pad as RetroArch index 2; Linux assigned it `js4`.
- The public RC8 installer downloaded its checksum-pinned package on the UNO Q, stopped and restarted App Lab, compiled and uploaded the matrix sketch, and served the updated Help and PDFs. Both console one-command upgrades passed with existing pairing retained. Batocera suspended and resumed EmulationStation, and its active Nestopia wrapper matched the packaged SHA-256. RetroPie mapped Player 2 to joystick 1, restarted its receiver, and kept the registered games on FCEUmm. The UNO Q listed both consoles online afterward.
- RetroPie then rebooted and returned with EmulationStation running, the receiver active, and its Player 2 mapping intact. Batocera was issued a reboot for the same recovery check, but remained unreachable at its previous IP address and `batocera.local` afterward; the UNO Q marked it offline. Its power and screen state require a physical check before final release.

## Games and input

- On Batocera, Gyromite and Stack-Up each launched with the FCEUmm and Nestopia wrappers. During each launch the UNO Q selected the exact game and reported a live frame link; exit cleared the session. Earlier live Direct-mode sessions decoded commands from both games.
- Batocera's EmulationStation mapping identifies the physical Atari controller as SDL joystick 0. The R.O.B. Vision virtual pad is joystick 2. The installed per-ROM configuration now assigns Player 1 to 0 and Player 2 to 2, with both ports using A=0 and B=1; Buddy's receiver swaps its Linux button events to match those logical buttons. The Batocera-specific autoconfiguration profile also uses A=0 and B=1. A clean installer upgrade preserved pairing and resumed EmulationStation.
- Automated Gyromite Game A screenshots with the production FCEUmm path measured the visible blue gate at vertical pixels 209–428 before a blue press, 356–576 during the hold, and 209–428 after release. A red-only hold left the blue gate at 209–428. This confirmed the Player 2 gamepad and blue gate return on the tested Batocera host.
- Nestopia interpreted RetroArch device `1` as Auto, allowing Gyromite's ROM to select its optical R.O.B. peripheral on Player 2. Its explicit gamepad device is `257`. The product wrapper now selects that gamepad after ROM load; the normal per-ROM configuration remains at device `1`. A wrapper rebuilt by the release workflow was installed on Batocera and tested in Game A: the blue gate occupied pixels 209–428 before a blue hold, 356–575 during it, and 209–428 after release. A red-only hold left the blue gate at 209–428. The temporary diagnostic core, options, and input mappings were removed.
- A repeat Batocera installer run suspended EmulationStation, installed the corrected wrapper, restarted its receiver, and resumed EmulationStation. The installed build and active core had the same SHA-256 digest, `7cef47a9c389283864a34716432835e533139c76436e1fbf47b5d396eeca54c9`.
- RetroPie's FCEUmm blue and red gates previously worked in Game A. With the corrected product Nestopia wrapper, RetroArch recorded Game A at 256×224 and 60 fps. At the first visible blue gate, a cyan column at x=69 occupied y=40–87 before the blue hold, y=64–110 and then y=72–119 during it, and y=40–87 after release. It stayed at y=40–87 during the later red-only hold. The normal FCEUmm selection and unrecorded launcher were restored afterward. Stack-Up Memory and Bingo remain outside the 0.1.0 gameplay claim.

## Automated checks

The Python suite, five JavaScript model tests, shell syntax, release checksum tests, and Git diff checks passed during candidate preparation. The repository and packages were scanned for tracked ROMs and known credential patterns. The corrected Nestopia wrapper built in the release workflow and passed the live Batocera Game A visual check. Stack-Up selected correctly with a live frame link through that wrapper; its earlier Direct-mode movement tests remain the movement evidence.

**Release decision:** Nestopia's Gyromite blue-gate return and the published RC8 one-command upgrades pass on both supported consoles. Hold final `v0.1.0` until Batocera boots and its receiver and emulator overlay recover after reboot.
