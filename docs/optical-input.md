# Optical game input from rendered NES frames

R.O.B. Vision reads the games' light messages from the emulator's rendered frames. There is no camera capture path in the current app. The light protocol still matters: Gyromite and Stack-Up encode left, right, up, down, open, close, and ready-light signals as 13 dark/green frame cells. See the [ROM analysis](ROM_SIGNAL_ANALYSIS.md) for the command tables.

## Frame classification and validation

The RetroPie wrapper observes each libretro video callback, classifies a grid of NES pixels as dark, green, or other, and forwards one classification and frame number to a local Unix socket. The receiver validates the sending process, wrapper path, and registered ROM. `ExactFrameDecoder` rejects missing frames, non-light frames inside a command, incomplete patterns, and commands belonging to another game. A complete game-specific command travels to the UNO Q's token-protected endpoint. Retries with the same sender PID and frame number apply once.

Test mode is separate from movement. `FrameTestDetector` recognizes a sustained green field in Gyromite or alternating dark/green frames in Stack-Up. A recent authenticated receiver heartbeat makes R.O.B.'s red light blink automatically. The ready-light command makes it steady for at most one second. Neither Test indication moves R.O.B.

## Current evidence and limits

Both games delivered all six command types during live FCEUmm Direct play. Nestopia delivered live movement commands from both games. The frame path does not depend on display refresh, a camera frame rate, or screen placement. It still requires the R.O.B. Vision emulator launch choice and exact registered ROM identity. Longer sessions, Stack-Up Memory/Bingo, and Nestopia's Gyromite gate return remain to be checked. See the [FCEUmm](FRAME_LINK_TEST_2026-09-25.md) and [Nestopia](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md) reports.

Dated Kiyo Pro and live camera reports in this repository document an abandoned research path; their measurements do not describe the current runtime.
