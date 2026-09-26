# R.O.B. Vision configuration reference

This reference lists the 0.1.x code defaults and installed settings. R.O.B. Vision uses console game frames for automatic input; it has no camera dependency. Host-specific validation results are in the [release report](RELEASE_VALIDATION_0.1.0.md).

| Setting | Current value or location | Meaning |
| --- | --- | --- |
| App Lab gateway | HTTP port 80 | `http://<uno-hostname>.local/dashboard/` or the UNO Q's LAN IP forwards to the controller. |
| Controller service | Port 8766 | Direct `/dashboard/` and `/api/` access. Local CLI binds loopback by default; use `--host 0.0.0.0` for a trusted LAN. |
| Controller token | UNO Q app `data/controller-token`, overridden by `ROB_VISION_TOKEN` when set | The installer creates and preserves the private file. Paired console credentials authenticate launch events, game-frame commands, and receiver polls. Browser controls on the trusted LAN do not use a token. |
| Gyro spin lifetime | 55 seconds | Illustrative virtual lifetime. |
| Fast Gate hold | 60 seconds maximum | Each manual Gyromite press automatically releases. |
| Browser state polling | 500 ms | `/api/state` snapshot; recent events capped at 30. |
| Console receiver polling | 50 ms; request timeout 250 ms | Root uinput service reads the UNO Q state. |
| Console stale release | 750 ms since last good response | Both virtual buttons release; game exit and missing RetroArch also release them. |
| Console process scan | 250 ms | Identifies an active RetroArch launch and can resync UNO Q game context, throttled to two seconds. |
| Game-frame socket | `/run/rob-vision/frames.sock` on RetroPie | The FCEUmm or Nestopia proxy sends one classified cell per rendered NES frame. The receiver verifies sender credentials, approved proxy path, ROM identity, and complete 13-frame commands. |
| RetroPie per-game NES choice | `lr-robvision-fceumm` or `lr-robvision-nestopia` | Both wrap the installed original core. The installer preserves an existing supported per-game choice, otherwise follows the NES default when available; unknown custom choices are left alone. Plain `lr-fceumm` and `lr-nestopia` bypass the link. The low-level `tools/install_retropie_frame_hook.py` accepts `--gyromite-core` and `--stack-up-core` for a per-game switch. |
| Game-frame indicator | Last matching receiver heartbeat within one second | `/api/state.input.frame_hook` is true. |
| Test signal indicator | Sustained green or alternating rendered frames | The receiver reports a recent signal automatically; the UNO Q blinks R.O.B.'s red light. |
| Batocera per-game NES choice | R.O.B. Vision FCEUmm or Nestopia for exact registered ROMs | Supported Batocera uses a runtime core overlay and per-ROM settings. An existing supported Nestopia choice is preserved; otherwise the installer selects FCEUmm. Unknown custom choices and unrelated games retain their settings. |
| Receiver online indicator | Authenticated poll within three seconds | Otherwise Setup and Mission show the relevant console offline. |
| Game registry | `<console install>/config/games.json` | Exact case-insensitive ROM basenames for Gyromite and Stack-Up. Edit through Setup → Game Registry; console upgrades preserve the file. |
| Registry editor | Console TCP port 8769; UNO Q `POST /api/games` | The paired UNO Q proxies bounded read/validate/save/restore requests. Saves require a closed game and an unchanged revision. |

## Release installation

The versioned installer URL and supported hardware are listed in the [installation guide](INSTALLATION_GUIDE.md). The Uno Q uses `uno-q`; both consoles use `console <Uno-Q-hostname>`. The same command upgrades an existing installation. Add `--pair` to the console command after revoking its credential in Setup. Batocera installation is based on available NES cores and a usable native frame wrapper, rather than a board or version allowlist.

## Local commands

```sh
python3 -m controller.service --host 127.0.0.1 --port 8766
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Gyromite (World).zip" ""
python3 tools/identify_game.py end
```

The optional standalone `deploy/rob-vision.service` must stay disabled while App Lab owns port 8766. App Lab runs one app at a time on this UNO Q. The repository includes UNO Q shutdown, early-start, and network-status host units; App Lab does not install them. Existing Avahi provides the UNO Q hostname as a `.local` address. See [UNO Q host helpers](../deploy/uno-q/README.md).
