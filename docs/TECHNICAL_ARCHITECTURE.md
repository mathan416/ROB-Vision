# R.O.B. Vision technical architecture

**Status, 25 September 2026:** The Arduino UNO Q runs the App Lab controller, matrix sketch, HTTP dashboard, and virtual R.O.B. model. RetroPie launch hooks and a paired virtual Controller 2 receiver run on `retropie.local`. FCEUmm delivered all six command types from both games during live Direct play; Nestopia delivered live commands from both games. Both Gyromite gate colors responded in Game A under FCEUmm. All robot parts are software state and graphics. No camera path remains.

## Runtime path

```text
RetroPie runcommand -- authenticated launch/exit --> UNO Q controller
NES frames --> FCEUmm or Nestopia wrapper --> local frame receiver
           --> authenticated command/Test signal --> UNO Q virtual model
                                                    +-- HTTP snapshot --> browser
                                                    +-- Gyromite pads --> RetroPie Controller 2
```

The App Lab `python/main.py` gateway publishes port 80 and forwards to `controller/service.py` on port 8766. Router Bridge sends controller status and action hints to `sketch/sketch.ino` for the UNO Q LED matrix. The dashboard polls `/api/state` every 500 ms. A local file preview uses a separate scripted JavaScript model; a served page with a controller enters live mode.

## Authority and state

`controller/service.py` owns the selected game, Test state, recent events, and virtual game models. `/api/state` schema 1 contains game, robot, input, events, link, and Test data. `input.frame_hook` reports a fresh RetroPie game-frame connection. Recent events are capped at 30 and are display history, not a durable event stream. Browser reload reads a new snapshot without resetting controller state.

`controller/model.py` keeps Gyromite's two gyros and Stack-Up's five blocks. Complete game-frame commands and manual commands pass through the same model. Invalid moves leave pieces in place. Stack-Up starts with all five blocks on Tray 3, and a grip may carry a block with those above it. Bingo's distinct starting layout is not implemented. Gyromite's 55-second spin lifetime and 60-second Fast Gate hold are illustrative settings.

The Gyromite pad reducer derives red and blue from gyro location/spin or a held unspun gyro. The RetroPie service polls the UNO Q, creates a Linux uinput controller, and applies states only while Gyromite is the active RetroArch game. It releases both buttons on exit, unknown game, missing process, failed authentication, or stale state. The verified port 2 mapping makes the dashboard's blue control move a blue gate and red control move a red gate under FCEUmm.

## Game-frame decoding

`rob_vision_fceumm_proxy.c` builds one wrapper for FCEUmm and one for Nestopia. Each delegates libretro API calls to the installed original core. Its video callback classifies each rendered NES frame as dark, green, or other and sends the frame number and class through a local Unix datagram socket. `retropie_frame_hook.py` verifies the sender's process credentials, approved wrapper path, and exact ROM identity. `controller/optical.py` accepts only complete game-appropriate 13-frame patterns. The receiver forwards commands to token-protected `/api/emulator/command`; retries are idempotent by sender PID and frame number.

The same classified frames recognize Gyromite's sustained green Test field or Stack-Up's alternating Test frames. The receiver reports a recent Test signal in its authenticated heartbeat, and the UNO Q blinks R.O.B.'s red light automatically. It returns to the game display after the signal stops. A separate READY command lights it steadily for at most one second, so a ready command sent while exiting Test cannot leave the matrix in T mode. Neither Test indication moves the model. FCEUmm remains selected for both registered games on the test RetroPie. Nestopia's Gyromite Player 2 return still needs a Game A check; see the [Nestopia report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md).

## Batocera host

Batocera 43.1 x86_64 uses the same frame decoder, UNO Q model, and uinput receiver. Its separate `ROBVision` service installs packaged x86_64 wrappers for stock FCEUmm and Nestopia in a runtime core overlay. The `zz-robvision-game` hook reports exact Gyromite/Stack-Up launch and exit events. It coexists with VirtualGlove's service, hook, and Super Glove Ball core. Batocera generates `retroarchcustom.cfg` after game-start hooks, so the service detects its virtual pad at startup and writes Gyromite-only `retroarch.*` per-ROM overrides to persistent `batocera.conf`. The Linux `/dev/input/jsN` number is not the RetroArch joystick index: during live 0.1.0 validation, the virtual pad was `js4` but RetroArch enumerated it as pad 2. The receiver now uses Batocera's SDL2 joystick order and writes that detected index with A button 1 and B button 0. In live RC6 testing, the pad emitted the expected events but Gyromite's Game A gate did not visibly move; that return path remains a release blocker.

Both console receivers identify themselves in authenticated heartbeats, launch events, and decoded commands. The UNO Q accepts frame commands from the active game's console and rejects the other. The inactive receiver releases its virtual Gyromite pad state. If both consoles are online, the status shows the active game's source; while idle, it may show either online receiver.

## HTTP and trust boundary

Trusted-LAN browser controls use `/api/game`, `/api/command`, and `/api/gate-assist` without a token. The browser reads `/api/state` and matrix status. JSON and same-origin checks protect browser writes. `/api/launch` and `/api/emulator/command` require the originating console's credential. Pairing uses a time-limited code and verified TLS certificate fingerprint to deliver it. Keep ports 80 and 8766 off untrusted networks.

## Resets and limits

Selecting a game or **Home** initializes its virtual pieces. Live **Emergency Stop** clears game selection; file preview cancels its local animation. Game exit clears context and releases buttons. The RetroPie receiver resends game identity after a UNO Q restart. It does not infer Hector's position, gate animation, Stack-Up score, or victory.

See [configuration](CONFIGURATION_REFERENCE.md), [network architecture](network-architecture.md), [frame input](optical-input.md), and the [verification plan](VERIFICATION_PLAN.md).

## 0.1.0 release installation path

`scripts/package_release.py` packages a committed Git tree under `rob-vision/`, calculates its SHA-256 digest, and renders `scripts/release-install.sh` with the release tag and digest. The release also carries four rebuilt PDF guides and `SHA256SUMS`. The downloaded installer checks the archive digest before extraction or platform mutation, detects `uno-q` or `console`, and calls the existing platform installer. Console detection distinguishes Batocera's persistent configuration and core paths from standard RetroPie. Batocera checks its version file and CPU architecture before writes; version 0.1.0 has validated wrappers for Batocera 43.1 x86_64 only.

The RetroPie installer copies its own `scripts` directory into `/home/pi/rob-vision`, enables the receiver unit, and preserves the private credential on upgrade. On first install the bootstrap starts `retropie_pair.py` as root. A successful certificate-pinned pairing enables and restarts the receiver and invokes the installed `player2` detector to write the actual joystick index to the NES RetroArch config. Both console installers install the virtual pad's udev RetroArch profile, which a clean system may lack. Batocera's installer suspends its EmulationStation process before stopping and replacing receiver modules, restarts `ROBVision`, and resumes the menu in a `finally` block. Pairing also restarts `ROBVision`, whose service writes Gyromite-only Player 2 overrides before gameplay. Both paths retain unrelated games and VirtualGlove configuration. The console command's optional `--pair` repeats pairing after a credential has been revoked in Setup.

The release installer requires curl, tar, Python 3, and SHA-256 tooling on the device. The Uno Q installer keeps its App Lab stop, stage, start, and rollback behavior. The release does not ship ROMs or vendor emulator cores.
