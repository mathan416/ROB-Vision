# Nestopia game-frame link verification, 25 September 2026

## What changed

The same libretro frame proxy can now be built for FCEUmm or Nestopia. RetroPie registers both `lr-robvision-fceumm` and `lr-robvision-nestopia`; the per-ROM installer retains each supported game's existing choice unless a core is named explicitly. The receiver accepts only these two exact proxy paths, a registered Gyromite or Stack-Up ROM, and a RetroArch process with its normal generated run configuration. The existing complete-pattern decoder and UNO Q command path are shared.

The authorized `retropie.local` test machine has both real cores and both proxy builds installed. Its Gyromite and Stack-Up selections were restored to FCEUmm after the Nestopia tests. The updated receiver service restarted and is active.

## Isolated game checks

To avoid interrupting the player's running Stack-Up game, a test-only Nestopia proxy was built with a separate Unix socket. A separate RetroArch process used a null video driver with threaded video disabled. Temporary input taps drove game menus and controls; they are not in the production proxy. The camera and the UNO Q model were not involved. The game ROMs were loaded from their existing `.7z` archives on RetroPie.

| Game | Observed Nestopia frames | Exact decoded commands |
| --- | --- | --- |
| Stack-Up | Test mode emitted alternating classified dark and green frames; a scripted Direct session emitted a complete command. | `UP_STACK` (`0001011111010`) |
| Gyromite | A scripted Direct session emitted complete command frames. | `RIGHT` (`0001011101010`), `LEFT` (`0001010111010`), `UP_GYRO` (`0001010111011`) |

The Nestopia core requested XRGB8888 pixels, which the existing frame classifier supports. Both games loaded and ran through the proxy without a production code change to the decoder. The first headless trial crashed before frame delivery; the unmodified Nestopia core crashed in the same headless configuration. Disabling threaded video in the isolated test configuration allowed both to run. This is a test harness setting, not a change to the RetroPie gameplay configuration.

## Live RetroPie and UNO Q checks

With no game running, the two per-ROM overrides were temporarily changed to Nestopia one game at a time. RetroPie's normal `runcommand.sh` selected `lr-robvision-nestopia` and launched each `.7z` ROM with its generated RetroArch configuration. A temporary Linux virtual keyboard pressed the user's mapped game keys; it was removed afterward. The receiver's process and ROM checks accepted each Nestopia process, and the UNO Q reported the matching selected game with `input.frame_hook = true`.

| Game | Receiver result | UNO Q result |
| --- | --- | --- |
| Stack-Up Direct | `LEFT` at frame 4328 | `Game frame decoded: LEFT`; `Emulator command: LEFT` |
| Gyromite Direct | `RIGHT` at frame 2416, `LEFT` at 2491, `UP_GYRO` at 2566 | Right and Left applied. Up was correctly blocked because the arms were already at the highest level. |

Each game was closed after its check. Both per-ROM choices were restored to `lr-robvision-fceumm`, the receiver service remained active, and the UNO Q cleared the game and frame-link state. The temporary input device and diagnostic files were removed from RetroPie.

## Remaining checks

These checks establish normal RetroPie launches, real Nestopia frame delivery, exact optical command decoding, and UNO Q model delivery in both games. Gyromite's Player 2 red/blue gate return has been confirmed under FCEUmm. Nestopia's blue-gate return was subsequently confirmed on RetroPie and Batocera in Game A; see the follow-ups below. Longer Nestopia sessions, Stack-Up Memory/Bingo, and colour behaviour with alternate Nestopia palettes or NTSC filters remain to be measured. FCEUmm remains the selected default.

## Batocera Game A follow-up

The Batocera 43.1 x86_64 test identified a separate Nestopia Player 2 issue. In Nestopia, libretro device `1` means Auto; Gyromite then connects its optical R.O.B. peripheral to the second port. Its explicit gamepad device is `257`. The wrapper now selects `257` after ROM load while the normal RetroArch configuration remains at `1`. The release workflow rebuilt the product wrapper, and a live Game A screenshot test measured the blue gate at pixels 209–428 before a blue hold, 356–575 during the hold, and 209–428 after release. A red-only hold left it at 209–428. Reinstalling the bundled wrapper on Batocera preserved its checksum and restarted the receiver and EmulationStation successfully. Stack-Up also selected correctly and reported a live frame link through this wrapper; previous Direct-mode tests establish its movement behaviour.

## RetroPie Game A follow-up

The corrected Nestopia wrapper was compiled and installed on `retropie.local`. Its receiver was upgraded and paired using the current console identity protocol. RetroPie's normal launcher selected the product Nestopia wrapper for Gyromite; the UNO Q reported Gyromite selected, the RetroPie console active, and game frames linked. RetroArch recorded the NES video at 256×224 and 60 fps while the UNO Q held blue, released blue, and held red alone. A cyan column of the first visible blue gate at x=69 occupied y=40–87 before the blue hold, y=64–110 and then y=72–119 during the hold, and y=40–87 after release. During the red-only hold it stayed at y=40–87. The per-game FCEUmm choice and unrecorded Nestopia launcher were restored after the test.

See [RetroPie setup](../deploy/retropie/README.md) for selecting either core and [FCEUmm live results](FRAME_LINK_TEST_2026-09-25.md) for the established end-to-end baseline.
