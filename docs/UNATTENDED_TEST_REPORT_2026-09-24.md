# Unattended two-game test report — 24 September 2026

These checks used the supplied Gyromite and Stack-Up ROM archives on RetroPie and the running R.O.B. Vision controller on the UNO Q. No ROM data was added to this repository. The existing Gyromite session on RetroPie was left running.

| Area | Gyromite | Stack-Up |
| --- | --- | --- |
| ROM identity | ZIP SHA-256 `bf1b323ba39c84b964f93127598b267ff3f16cbf99c533ae1e9b8332232b3e5b`; analyzer found seven optical entries. | ZIP SHA-256 `3ab6bc99246783a6bf7083481027fe358ccdb147dcf1165eaf08aaf4e1b06548`; analyzer found six commands. |
| Emulator boot | Existing `.7z` game remained running in RetroArch throughout verification. | ZIP loaded under FCEUmm in RetroArch with null video/input/audio drivers; the process ran until the planned eight-second timeout. This confirms boot, not visible gameplay. |
| Game detection | Live RetroPie process was recognized. After a UNO Q restart had cleared the selected game, the receiver restored `gyromite` through the authenticated launch endpoint. | Exact Stack-Up process command was recognized in an isolated test; its live EmulationStation launch was not attempted. |
| Camera command to virtual action | Automated 240 fps light traces moved a gyro from holder to spinner to red pad; spin and pad state changed, then lifting released red. | Automated 240 fps light traces moved red alone, then blue and white together onto red. A blocked move preserved state; all five blocks remained accounted for. |
| Wrong-game commands | Stack-Up vertical command left Gyromite state unchanged. | Gyromite vertical command left Stack-Up state unchanged. |
| Idle/Test false triggers | Thirty seconds each of dark idle with brightness noise and alternating Test flashes generated zero commands. | Same: zero commands. |

Local checks: 29 Python unit tests and five JavaScript Stack-Up model tests passed. The receiver service was active on RetroPie afterward; the UNO Q reported `gyromite`, receiver online, both pads released, and camera offline.

## Camera timing finding

In a deterministic synthetic stress run (100 traces for each command, random camera phase, ±0.7 ms timestamp jitter, small brightness noise), the current run-duration decoder missed some valid transmissions. At 60 fps it decoded 661/700 Gyromite and 186/200 Stack-Up commands; at 90 fps, 687/700 and 200/200; at 120 fps, 617/700 and 175/200; at 240 fps, 700/700 and 200/200. The non-monotonic results reflect ambiguous measured run lengths near a half-frame boundary. A proposed fallback performed worse and was discarded. These are synthetic results, not a camera acceptance test; they indicate that an actual camera/display timing calibration is necessary before relying on optical play.

**Camera-rate correction (24 September):** the intended camera will deliver at most 60 fps, so the 90/120/240 fps results above are diagnostic comparisons, not target modes. A reproducible 30/60 fps stress test with a separate seed and 900 transmissions found 0/900 accepted at 30 fps. At 60 fps, the original decoder accepted 839/900 but occasionally reported the wrong command. An additional sampled-frame ambiguity check now rejects traces that could mean more than one action: 667/900 were accepted correctly, 233/900 were rejected, and none were misclassified in this run. Ten further 900-transmission seeds also produced no wrong actions. Some 60 fps misses correspond to an entire one-frame flash falling between two captures. The controller now requests 60 fps rather than 120 fps; this is only a driver request, and the delivered rate remains the meaningful value. A reliable fallback may require an emulator-side command hook if the real camera/display combination exhibits those misses.

## Remaining checks with hardware

- Attach and position the intended camera on the UNO Q; confirm Test flashes, command recognition, and false-trigger rate on the target LCD/OLED at its actual measured capture rate.
- Observe a real Stack-Up interactive launch and its on-screen responses to the six commands.
- Confirm live Gyromite red/blue gate movement after optical recognition, including release on link loss. Previous user-observed gate checks used browser controls rather than camera decoding.
- Confirm the UNO Q matrix animations by eye; software state and bridge transport have been checked, but the LEDs have not been visually observed for each mode.
