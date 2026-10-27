# R.O.B. Vision configuration reference

This reference lists the 0.1.x code defaults and installed settings. R.O.B. Vision uses console game frames for automatic input; it has no camera dependency. Host-specific validation results are in the [release report](RELEASE_VALIDATION_0.1.0.md).

| Setting | Current value or location | Meaning |
| --- | --- | --- |
| Controller Router entry page | HTTP port 80 | Opens the sole installed product, or shows a chooser when both are installed. |
| R.O.B. Vision browser | HTTP port 8101 | Mission at `/dashboard/`, Setup at `/dashboard/setup.html`, and Help at `/dashboard/help.html`. **Apps** appears only with two installed products. |
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
| Receiver online indicator | Authenticated poll within three seconds | The UI reports **Receiver Waiting** when check-ins are absent; this does not establish whether the console is powered off. |
| Game registry | `<console install>/config/games.json` | Exact case-insensitive ROM basenames for Gyromite and Stack-Up. Edit through Setup → Game Registry; console upgrades preserve the file. |
| Router input lease | Refreshed about every 250 ms; valid for two seconds | The selected product may produce console input. Missing, malformed, expired, or previous-boot leases are rejected on Router-managed installs. |
| Queued command retention | Up to 12 seconds; HTTP retry every 200 ms | Keeps commands through initial Router selection; discards expired commands, a changed game/source, or a departed wrapper process. |
| Live session expiry | Ten seconds without an authenticated receiver check-in | Clears the active game so Router can return to neutral. |
| Registry editor | Console TCP port 8769; UNO Q `POST /api/games` | The paired UNO Q proxies bounded read/validate/save/restore requests. Saves require a closed game and an unchanged revision. |

## Release installation

The versioned installer URL and supported hardware are listed in the [installation guide](INSTALLATION_GUIDE.md). The Uno Q uses `uno-q`; both consoles use `console <Uno-Q-hostname>`. The same command upgrades an existing installation. Add `--pair` to the console command after revoking its credential in Setup. Batocera installation is based on available NES cores and a usable native frame wrapper, rather than a board or version allowlist.

## Local commands

```sh
python3 -m controller.service --host 127.0.0.1 --port 8766
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Gyromite (World).zip" ""
python3 tools/identify_game.py end
```

The optional standalone `deploy/rob-vision.service` must stay disabled while App Lab owns port 8766. Controller Router owns the sole App Lab Matrix sketch; both product Linux services run continuously in separate Compose projects. The repository includes UNO Q shutdown, early-start, and network-status host units; App Lab does not install them. Existing Avahi provides the UNO Q hostname as a `.local` address. See [UNO Q host helpers](../deploy/uno-q/README.md).

## Installer prerequisites and architecture support

The release bootstrap requires `curl`, `tar`, Python 3 and `sha256sum` or `shasum`. UNO Q installation expects App Lab, the `arduino` account, Docker Compose and Python 3.9 or newer. Standard RetroPie needs Python 3.7+, `gcc`, `openssl`, `sudo`, systemd, `uinput` and an installed NES core (`lr-fceumm` or `lr-nestopia`). Batocera needs Python 3.9+, its service manager, SDL2 and an installed FCEUmm or Nestopia core. Recalbox 10.x needs Python 3, `/dev/uinput`, and an installed FCEUmm or Nestopia Libretro core. The installer load-tests its packaged wrapper for the device. Recalbox 10.1.1 on the `rpizero2` target passed bounded game launches; other targets need matching wrapper and device validation.

Batocera support is checked by capability, not a board/version allowlist. Packaged wrappers cover x86_64, x86, AArch64, ARMv7, ARMv6 and RISC-V 64. The installer tests whether a matching wrapper loads and can compile one when a native compiler is available. Architecture coverage is distinct from live validation; the dated release and frame-link reports record tested hardware.

RetroPie installer migrations may remove a recognised old Router index block and register the launch adapter in `emulators.cfg`. Saved `retroarch.cfg` files are not changed at receiver startup or game launch. Installer-owned RetroPie configuration writes preserve `pi:pi` ownership.

## Shared device pairing

Controller Router is the connection authority. The UNO Q host broker runs secure Setup on TCP **8444** and stores schema-1 connections under `/home/arduino/.local/state/controller-router/connections.json`. The persistent console TLS service listens on TCP **55359**. Router has a management credential; VirtualGlove and R.O.B. Vision have distinct, independently revocable credentials. Browser responses contain only public connection and readiness fields.

`router_shared.pairing.Peer` checks the console certificate before sending a code or credential. The CR1 code contains a 100-bit certificate fingerprint prefix and a 60-bit authorization value. Console windows last 300 seconds, accept one successful transaction, and lock after five incorrect codes. Physical Matrix confirmation lasts 120 seconds and allows five attempts. Requests are bounded; servers allow at most 16 concurrent workers and require TLS 1.2 or later. Secure browser writes require matching HTTPS Origin, a fixed action header, and JSON content.

Provisioning uses prepare, commit, and finalize. Private journals retain the previous Router registry and app configuration; interrupted or failed transactions restore those snapshots. Successful changes keep private before-connection backups. Legacy migration verifies an HMAC over a fresh nonce, canonical console ID, and observed TLS certificate; adoption signs the new connection transcript. Hostnames alone never authorize consolidation. Conflicting records remain unchanged for an explicit re-pairing choice.

Products expose `/api/router-pairing` only to a capability-bearing local host request. Capability files are named `data/router-pairing-adapter-token` and must not be exposed to browsers. Adapters import app credentials into live caches without replacing ROM registries, calibration, or player settings. Router polls for newly installed console and UNO adapters and provisions them using its pinned management connection. Disabled app access stays disabled.

The console helper has `/identity`, `/pair`, `/legacy-proof`, `/adopt`, `/manage`, and `/router` interfaces. `/manage` uses Router's credential for inspection, provisioning, and removal. `/router` uses the same credential with `RouterStore` revision checks for assignments and system policy. It never writes saved RetroArch configurations. Buddy's first-pair adapter adds only its Player 2 source to Router configuration; emulator configuration migration remains installation-only.

Back up the UNO Q connection registry, its `tls` directory, and the private before-connection backups. On RetroPie, also back up `/var/lib/controller-router/link/{console-id,adapters.json,connection.json,certificate.pem,private-key.pem}` and each product's credential files. Restore requires the separately installed shared link service. Keep backups private; never include credentials in diagnostics or support reports. Do not snapshot a provisioning transaction in progress.
