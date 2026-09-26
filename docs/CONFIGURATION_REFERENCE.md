# R.O.B. Vision configuration reference

This reference lists the 0.1.x code defaults and installed settings. R.O.B. Vision uses console game frames for automatic input; it has no camera dependency. Host-specific validation results are in the [release report](RELEASE_VALIDATION_0.1.0.md).

| Setting | Current value or location | Meaning |
| --- | --- | --- |
| App Lab gateway | HTTP port 80 | `http://arduiain.local/dashboard/` forwards to the controller. |
| Controller service | Port 8766 | Direct `/dashboard/` and `/api/` access. Local CLI binds loopback by default; use `--host 0.0.0.0` for a trusted LAN. |
| Controller token | UNO Q app `data/controller-token`, overridden by `ROB_VISION_TOKEN` when set | The installer creates and preserves the private file. It authenticates RetroPie launch events, game-frame commands, and receiver polls. Browser controls on the trusted LAN do not use it. |
| Gyro spin lifetime | 55 seconds | Illustrative virtual lifetime. |
| Fast Gate hold | 60 seconds maximum | Each manual Gyromite press automatically releases. |
| Browser state polling | 500 ms | `/api/state` snapshot; recent events capped at 30. |
| RetroPie receiver polling | 50 ms; request timeout 250 ms | Root uinput service reads the UNO Q state. |
| RetroPie stale release | 750 ms since last good response | Both virtual buttons release; game exit and missing RetroArch also release them. |
| RetroPie process scan | 250 ms | Identifies an active RetroArch launch and can resync UNO Q game context, throttled to two seconds. |
| RetroPie game-frame socket | `/run/rob-vision/frames.sock` | The FCEUmm or Nestopia proxy sends one classified cell per rendered NES frame. The receiver verifies sender credentials, approved proxy path, ROM identity, and complete 13-frame commands. |
| RetroPie per-game NES choice | `lr-robvision-fceumm` or `lr-robvision-nestopia` | Both use the installed original core through the frame wrapper. Current Gyromite and Stack-Up selections remain FCEUmm. Plain `lr-fceumm` and `lr-nestopia` bypass the link. For a per-game core switch after installation, the low-level `tools/install_retropie_frame_hook.py` accepts `--gyromite-core` and `--stack-up-core`. |
| Game-frame indicator | Last matching receiver heartbeat within one second | `/api/state.input.frame_hook` is true. |
| Test signal indicator | Sustained green or alternating rendered frames | The receiver reports a recent signal automatically; the UNO Q blinks R.O.B.'s red light. |
| Receiver online indicator | Authenticated poll within three seconds | Otherwise Setup and Mission show RetroPie offline. |
| Game registry | `config/games.json` | Exact case-insensitive ROM basenames for Gyromite and Stack-Up, including configured ZIP, 7z, and NES names. |

## Release installation

The versioned installer URL and supported hardware are listed in the [installation guide](INSTALLATION_GUIDE.md). The Uno Q uses `uno-q`; both consoles use `console <Uno-Q-hostname>`. The same command upgrades an existing installation. Add `--pair` to the console command after revoking its credential in Setup. Batocera 43.1 x86_64 is the validated Batocera build; other board/version combinations are rejected before installation.

## Local commands

```sh
python3 -m controller.service --host 127.0.0.1 --port 8766
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Gyromite (World).zip" ""
python3 tools/identify_game.py end
```

The optional standalone `deploy/rob-vision.service` must stay disabled while App Lab owns port 8766. App Lab runs one app at a time on this UNO Q. The repository includes UNO Q shutdown, early-start, and network-status host units; App Lab does not install them. Existing Avahi provides `arduiain.local`. See [UNO Q host helpers](../deploy/uno-q/README.md).
