# R.O.B. Vision technical architecture

**Status, 25 September 2026:** The Arduino UNO Q runs the App Lab controller, matrix sketch, HTTP dashboard, and virtual R.O.B. model. RetroPie launch hooks and a paired virtual Controller 2 receiver run on `retropie.local`. Both Gyromite gate colors responded in Game A. The attached camera recognized both games' Test modes at about 60 fps. Live Stack-Up camera flashes were intermittent. The RetroArch frame link decoded all six command types during live Direct play in both games. Gyromite lift, rotation, and grip, plus Stack-Up grip, lift, and rotation, updated the UNO Q model. R.O.B. and all accessories exist only in software.

## Runtime path

```text
RetroPie runcommand -- authenticated launch/exit --> UNO Q controller
Game display -- light flashes --> UNO Q camera --> optical decoder
                                            --> virtual model
                                                +-- HTTP snapshot --> browser
                                                +-- Gyromite pads --> RetroPie
                                                    virtual Controller 2
FCEUmm game frames -- local RetroPie frame receiver
                   -- authenticated command --> UNO Q virtual model
```

The App Lab `python/main.py` publishes port 80 and forwards to `controller/service.py` on port 8766. Its Router Bridge sends controller status and action hints to `sketch/sketch.ino` for the UNO Q LED matrix. The dashboard polls `/api/state` every 500 ms. The local file preview uses its separate JavaScript demonstration model; a served page with an available controller enters live mode.

## Authority and state

`controller/service.py` owns the selected game, camera/Test status, recent events, and virtual game models. `/api/state` is a snapshot with schema version 1, game, robot, camera, input, recent events, link, and Test data. `input.frame_hook` reports a fresh RetroPie game-frame connection. Recent events are capped at 30; they are display history, not a durable event stream. There is no session ID or WebSocket. Reopening the browser reads a fresh snapshot without resetting the controller.

`controller/model.py` keeps Gyromite's two gyros and Stack-Up's five blocks. A complete optical command or operator command passes through the same model. Invalid moves return an error and leave piece state intact. Stack-Up starts with all five blocks on Tray 3; a grip can carry a block with those above it, preserving order. The current live model uses this initial layout for all modes; mode-specific Bingo layouts are not implemented. Gyromite's 55-second spin lifetime and 60-second Fast Gate hold are simulation settings, not measured Nintendo hardware properties.

The Gyromite pad reducer derives red and blue from gyro location/spin or a held unspun gyro. The RetroPie service polls the UNO Q, creates a Linux uinput controller, and applies the current states only while Gyromite is the active RetroArch game. It releases both buttons on exit, unknown game, missing process, failed authentication, or stale state. The verified RetroArch port 2 mapping makes the dashboard's blue control move a blue gate and red control move a red gate.

## Optical capture

`controller/optical.py` recognizes the ROM-derived six movement/grip patterns from timestamped bright/dark camera samples. `controller/service.py` optionally opens an OpenCV capture device, requests 60 fps, samples the central 60% by default, and reports measured fps. A sustained green field or regular Test alternation drives the red status light without moving R.O.B. Synthetic 60 fps jitter runs yielded 667 correct and 233 rejected commands out of 900, with zero wrong commands in that run. At 30 fps, all 900 were rejected.

For RetroPie, `rob_vision_fceumm_proxy.c` is built once for FCEUmm and once for Nestopia. Each build delegates the libretro core API to the corresponding installed core and observes each rendered NES frame before display. It sends only the frame number and black/green/other classification through a local Unix datagram socket. `retropie_frame_hook.py` checks the sender process credentials, either approved proxy path, and ROM registry, then accepts only a complete, game-appropriate 13-frame pattern. The paired RetroPie receiver sends the command to the UNO Q's token-protected `/api/emulator/command` endpoint; retry idempotency is keyed by sender PID and frame number. While this link is fresh, camera movement decoding is suppressed to prevent duplicate actions; camera preview and Test detection remain available. If the link stops, camera movement decoding resumes. The installed per-ROM RetroPie choices keep FCEUmm selected for Gyromite and Stack-Up until changed; both R.O.B. proxy core choices are available, and other NES games keep the normal default core. All six command types were observed live with FCEUmm in both games. Nestopia also delivered live Stack-Up and Gyromite movement commands to the UNO Q. Gyromite's Player 2 gate return under Nestopia remains to be verified. See the [Nestopia test report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md).

## HTTP and trust boundary

Browser controls on the trusted LAN can call `/api/game`, `/api/command`, `/api/gate-assist`, `/api/test/arm`, and camera actions without a token. The browser also reads `/api/state`, `/api/camera/frame`, and matrix status. The service uses JSON and same-origin checks for browser writes. `/api/launch` and receiver identity require the shared token; pairing uses a time-limited code and verified TLS certificate fingerprint to deliver it. Do not expose port 80 or 8766 to an untrusted network.

Setup's **Reset & Reconnect** closes and reopens OpenCV capture; it does not reset the USB hub. UNO Q host recovery units are supplied under `deploy/uno-q` but are not installed by App Lab and currently need separate privileged setup. The attached Razer Kiyo Pro runs at 640×480 MJPEG near 60 delivered fps after a temporary, identity-checked HDR-off and 1 ms manual exposure request. Stack-Up has confirmed live RIGHT and DOWN optical movements; repeated capture reliability and Gyromite movement still need confirmation.

## Resets and limits

Selecting a game or **Home** initializes that game's virtual pieces. **Emergency Stop** in live mode stops camera capture and clears the selected game; in the file preview it cancels its local animation. Game exit clears context and releases buttons. The RetroPie receiver also scans the running RetroArch process and resends game identity after a UNO Q restart. It does not infer Hector's position, gate animation, Stack-Up score, or game victory.

See [configuration](CONFIGURATION_REFERENCE.md), [network architecture](network-architecture.md), [optical input](optical-input.md), and the [verification report](UNATTENDED_TEST_REPORT_2026-09-24.md).
