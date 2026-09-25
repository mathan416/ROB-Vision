# Gyromite and Stack-Up ROM signal analysis

**Status:** Static analysis of the user-supplied `Gyromite (World)` and `Stack-Up (World)` ROMs, 24 September 2026. The ZIP and 7z copies of each game contain identical NES data. No ROM or extracted graphics is stored in this project. The derived patterns are decoded from RetroPie rendered NES frames by the FCEUmm and Nestopia frame-link wrappers.

Run `python3 tools/analyze_rob_roms.py --gyromite '/path/to/Gyromite (World).zip' --stack-up '/path/to/Stack-Up (World).zip'` to reproduce the command report from the archives in place. The program rejects unexpected ROM layout or changed evidence bytes. The inspected full-file SHA-256 hashes are `bf1b323ba39c84b964f93127598b267ff3f16cbf99c533ae1e9b8332232b3e5b` (Gyromite) and `3ab6bc99246783a6bf7083481027fe358ccdb147dcf1165eaf08aaf4e1b06548` (Stack-Up). Each is an iNES mapper-0 image with 32 KiB program ROM and 8 KiB character ROM.

## What the games transmit

The screen flashes represent **one robot primitive per command**, not a complete task such as “move the red gyro to its tray” or “solve this Stack-Up pattern.” A 13-frame message has the form:

```text
000101w1x1y1z
```

`0` is the dark frame (NES palette `$0F`), `1` is the green frame (`$2A`), and `wxyz` selects an action. The pattern is consistent with the independently documented [NESdev R.O.B. interface](https://www.nesdev.org/wiki/R.O.B.) and [original hardware protocol research](https://github.com/zfields/nes-rob/blob/main/docs/research.md). At a roughly 60 Hz NES video rate, the 13 data frames span about 217 ms; the final visible duration and gaps still depend on emulator and display behavior. Stack-Up's transmission routine schedules an additional dark frame after the 13 data frames.

| Action | `wxyz` | Full 13-frame pattern | Gyromite | Stack-Up |
| --- | --- | --- | --- | --- |
| Open grippers | `1010` | `0001011101110` | Yes | Yes |
| Close grippers | `0110` | `0001010111110` | Yes | Yes |
| Turn left one station | `0100` | `0001010111010` | Yes | Yes |
| Turn right one station | `1000` | `0001011101010` | Yes | Yes |
| Raise two levels | `0101` | `0001010111011` | Yes | No |
| Lower two levels | `1101` | `0001011111011` | Yes | No |
| Raise one level | `1100` | `0001011111010` | No gameplay table | Yes |
| Lower one level | `0010` | `0001010101110` | No gameplay table | Yes |
| Head ready light on | `1001` | `0001011101011` | ROM command table | Stack-Up test path |

The eight-bit command byte is the message after the five leading bits: for example, open is `$EE`, close `$BE`, left `$BA`, right `$EA`, Gyromite up/down `$BB/$FB`, Stack-Up up/down `$FA/$AE`, and ready light `$EB`. The ready-light message is a status operation. It must never move an axis.

Gyromite Test produces a sustained green signal. Stack-Up Test alternates green and dark frames on the ROBOT BLOCK artwork. The frame-link Test detector can blink the virtual head light when the check is armed; a separately decoded ready-light command produces a steady light. These are status indications, not motion commands.

### ROM evidence

- **Gyromite:** The program at `$A679–$A697` indexes a palette-choice table at `$A6FC`, with 13 entries per command slot and the entries read in reverse order. Valid populated slots 1, 2, 3, 5, 6, 7, and 8 decode to the rows above. Slot 4 is deliberately skipped in the controller selection logic at `$A591–$A5A2`; its table area is not a valid optical command. Palette-selection values 3 and 4 resolve through the table at `$B35E` to the all-black palette at `$B404` and all-green palette at `$B428` respectively. This ties the table bits to actual on-screen light, rather than just matching known codes by coincidence.
- **Stack-Up:** The routine at `$B1DE` starts a transmission and `$B1E7–$B237` builds successive frames. It uses the template at `$B24A`: six fixed preamble bits followed by four variable bits separated by fixed green bits. The variable bits come least-significant-bit first from command values 1–6. Palette selections 2 and 3 point via `$82E8` to the black and green palettes at `$B598/$B5AC`. The ROM's final loop pass is an extra dark frame. A separate test path calls the sender with value 9 for the head light; that is not a movement command.
- **Cross-check:** The byte patterns and action names agree with the [NESdev hardware interface](https://www.nesdev.org/wiki/R.O.B.). The original [Nintendo photosensing patent](https://patents.google.com/patent/US4815733A/en) describes frame-aligned light code transmission, but this report's per-game command table comes from the supplied ROMs.

These addresses refer to the CPU view of these exact 32 KiB program images (`$8000–$FFFF`). The static analysis establishes the encoded message and palette choices. It does not establish every mode-specific command cadence.

## Implemented frame decoder

The FCEUmm and Nestopia wrappers classify each rendered NES frame as dark, green, or other. The local RetroPie receiver uses the verified game identity and complete frame numbers to decode the 13-frame patterns above. It forwards accepted commands to the UNO Q over the paired HTTP link. Incomplete patterns, gaps, unexpected frame classes, and actions outside the selected game's allowed set do not move R.O.B. The ready-light command and Test-mode signal update status only. Separate identical commands remain valid.

Game identification follows the exact launch-filename registry described in [Game Identification](GAME_IDENTIFICATION.md). It selects the allowed action set and virtual accessory profile; a launch event by itself does not imply a decoded command. Mission reports link activity and accepted or blocked actions.

## Implemented virtual action mapping

Every accepted optical message advances **one bounded virtual primitive**. The UNO Q owns the virtual state and the browser animates it. No physical motion controller is part of this design.

| Optical event | Robot operation | Display/state requirement |
| --- | --- | --- |
| Left / right | Rotate one virtual station | Update station and fixture occupancy; the browser animates the resulting pose. |
| Gyromite up / down | Move two virtual vertical levels | Move two levels and reject an out-of-range target. |
| Stack-Up up / down | Move one virtual vertical level | Move one level and update held-block state. |
| Open / close | Open or close the illustrated grippers once | Update a piece only when the modeled grasp or release is valid. |
| Ready-light / test | Update optical or visual readiness only | Never move virtual pieces. |

For **Gyromite**, a sequence of these primitives transfers a virtual gyro between holder, spinner, red pad, and blue pad. The UNO Q derives virtual pad state from its object model and sends that state to the paired LAN Controller 2 receiver. The flash stream alone does not identify the professor's location or prove that the game accepted the returned button. The model tracks which gyro is held and which pad is pressed.

For **Stack-Up**, the same primitives manipulate five virtual colored blocks across five numbered trays. The pose also includes six height levels; closing at a lower block can carry it and every block above it as an ordered segment. The flash stream has no block ID, target-pattern, or victory message. The UNO Q can know its own modeled stack state, but not the game's desired pattern without another validated source. Memory mode may send rapid commands; the current controller has no queue or explicit missed-command state, so this cadence needs a sustained live frame-link test. In the Bingo simultaneous row-and-column case described in the manual, the game sends no command until one line changes; the frame link should yield no valid movement message.

## Next validation gate

Exercise all nine patterns above, idle, Test, Stack-Up Memory speeds, and the Bingo no-command case through both supported wrappers. Compare observed frame classes against the ROM-derived rows and measure missed commands, false actions, and spacing under long sessions.
