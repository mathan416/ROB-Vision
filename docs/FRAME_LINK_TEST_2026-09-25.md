# RetroPie game-frame link verification, 25 September 2026

## Purpose

The Kiyo Pro delivered roughly 60 camera frames per second, but some one-frame light cells were missed. This test checks an alternate path that observes the NES image once per emulated frame inside RetroArch. It tests game command identity and UNO Q model actions; it does not measure camera-only reliability.

## Installed path

RetroPie selects `lr-robvision-fceumm` only for the registered Gyromite and Stack-Up ROM names. The proxy delegates normal libretro operation to the installed FCEUmm core. Its video callback classifies each rendered frame as dark, green, or other and sends the frame number and class through `/run/rob-vision/frames.sock`. The paired receiver verifies Unix sender credentials, RetroArch's command line, the proxy core path, and the ROM registry. It accepts only a complete 13-frame pattern appropriate to that game, then sends the command to the UNO Q using the existing receiver token. The UNO Q applies the command to the same virtual model used by manual controls. While the frame link is fresh, camera movement decoding pauses to prevent duplicate actions; camera preview and Test detection continue.

The tested ROMs were `Gyromite (World).7z` and `Stack-Up (World).7z`, launched from EmulationStation. Both RetroArch processes used the proxy core, and `/api/state.input.frame_hook` was true while each ran. The ordinary NES default core was left as FCEUmm.

## Live results

| Game | Commands observed from game frames | UNO Q result |
| --- | --- | --- |
| Gyromite Direct | DOWN_GYRO, UP_GYRO, LEFT, RIGHT, OPEN, CLOSE | Lift moved 6 → 4 → 6, station moved 2 → 1 → 2, and the hands closed then reopened. An initial OPEN while already open was correctly blocked. |
| Stack-Up Direct | CLOSE, DOWN_STACK, OPEN, LEFT, UP_STACK, RIGHT | Hands closed and reopened, lift moved 6 → 5 → 6, and station changed as directed. An initial UP at maximum height was correctly blocked. |

Commands were triggered through the configured Player 1 input on RetroPie, without manually issuing model commands. The receiver journal recorded the complete decoded names and source frame numbers. The UNO Q Activity Feed recorded matching `Game frame decoded` and `Emulator command` events, and `/api/state` showed the resulting pose. For example, Gyromite DOWN_GYRO was decoded at frame 3678 and UP_GYRO at frame 4681; Stack-Up DOWN_STACK was decoded at frame 12121 and UP_STACK at frame 13644 in the second Direct session.

The first Stack-Up trial used an overly strict whole-frame green classifier. Test artwork contains dark borders, so green Test frames were classified as other. Sampling the central picture area as well corrected the class sequence. After that change, both games' ROM-derived 13-frame messages decoded exactly. No idle or Test-only transmission produced an unintended movement during these sessions.

## Operational checks

- The receiver remained paired and online; the frame-link indicator remained active after its service was restarted with temporary trace logging disabled.
- The UNO Q's camera preview was restored after its controller restart. The new input path did not require camera capture to be running.
- RetroPie continued to launch and exit games through the existing runcommand hooks. The per-ROM core selection worked for `.7z` archives.
- Temporary RetroArch network commands and per-frame journal tracing were removed from the running configuration. The live Stack-Up game was left running for the player.
- The local test suite passed 48 tests, including complete-pattern decoding, sender/ROM checks, retry idempotency, and per-ROM installation behavior.

## Limits and next verification

These are functional end-to-end tests, not a long-session reliability measurement. The source sends a full command in 13 consecutive emulated frames; the receiver rejects gaps and partial patterns. Stack-Up Memory and Bingo timing, game exit/relaunch endurance, alternate display/video settings, and repeated full-game sessions have not been measured. The frame link reports commands, not Hector's location, score, or target block order. Camera-only decoding remains experimental for original hardware or other game hosts.
