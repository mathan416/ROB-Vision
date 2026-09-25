# R.O.B. Vision technical architecture

**Status, 25 September 2026:** The Arduino UNO Q runs the App Lab controller, matrix sketch, HTTP dashboard, and virtual R.O.B. model. RetroPie launch hooks and a paired virtual Controller 2 receiver run on `retropie.local`. Both Gyromite gate colors responded in Game A. The attached camera recognized both games' Test modes at about 60 fps. One live Stack-Up RIGHT flash decoded and moved the virtual R.O.B. one station; later flashes were missed, so automatic optical play is not yet reliable. R.O.B. and all accessories exist only in software.

## Runtime path

```text
RetroPie runcommand -- authenticated launch/exit --> UNO Q controller
Game display -- light flashes --> UNO Q camera --> optical decoder
                                            --> virtual model
                                                +-- HTTP snapshot --> browser
                                                +-- Gyromite pads --> RetroPie
                                                    virtual Controller 2
```

The App Lab `python/main.py` publishes port 80 and forwards to `controller/service.py` on port 8766. Its Router Bridge sends controller status and action hints to `sketch/sketch.ino` for the UNO Q LED matrix. The dashboard polls `/api/state` every 500 ms. The local file preview uses its separate JavaScript demonstration model; a served page with an available controller enters live mode.

## Authority and state

`controller/service.py` owns the selected game, camera/Test status, recent events, and virtual game models. `/api/state` is a snapshot with schema version 1, game, robot, camera, recent events, link, and Test data. Recent events are capped at 30; they are display history, not a durable event stream. There is no session ID, command queue, WebSocket, or emulator game-state hook. Reopening the browser reads a fresh snapshot without resetting the controller.

`controller/model.py` keeps Gyromite's two gyros and Stack-Up's five blocks. A complete optical command or operator command passes through the same model. Invalid moves return an error and leave piece state intact. Stack-Up starts with all five blocks on Tray 3; a grip can carry a block with those above it, preserving order. The current live model uses this initial layout for all modes; mode-specific Bingo layouts are not implemented. Gyromite's 55-second spin lifetime and 60-second Fast Gate hold are simulation settings, not measured Nintendo hardware properties.

The Gyromite pad reducer derives red and blue from gyro location/spin or a held unspun gyro. The RetroPie service polls the UNO Q, creates a Linux uinput controller, and applies the current states only while Gyromite is the active RetroArch game. It releases both buttons on exit, unknown game, missing process, failed authentication, or stale state. The verified RetroArch port 2 mapping makes the dashboard's blue control move a blue gate and red control move a red gate.

## Optical capture

`controller/optical.py` recognizes the ROM-derived six movement/grip patterns from timestamped bright/dark samples. `controller/service.py` optionally opens an OpenCV capture device, requests 60 fps, samples the central 60% by default, and reports measured fps. A sustained green field or regular Test alternation drives the red status light without moving R.O.B. A complete valid command drives one action; ambiguous or partial traces drive none. Synthetic 60 fps jitter runs yielded 667 correct and 233 rejected commands out of 900, with zero wrong commands in that run. At 30 fps, all 900 were rejected. This is a decoder result, not a live camera acceptance result. An emulator hook is an unimplemented fallback if camera timing proves inadequate.

## HTTP and trust boundary

Browser controls on the trusted LAN can call `/api/game`, `/api/command`, `/api/gate-assist`, `/api/test/arm`, and camera actions without a token. The browser also reads `/api/state`, `/api/camera/frame`, and matrix status. The service uses JSON and same-origin checks for browser writes. `/api/launch` and receiver identity require the shared token; pairing uses a time-limited code and verified TLS certificate fingerprint to deliver it. Do not expose port 80 or 8766 to an untrusted network.

Setup's **Reset & Reconnect** closes and reopens OpenCV capture; it does not reset the USB hub. UNO Q host recovery units are supplied under `deploy/uno-q` but are not installed by App Lab and currently need separate privileged setup. The attached Razer Kiyo Pro runs at 640×480 MJPEG near 60 delivered fps after a temporary, identity-checked HDR-off and 1 ms manual exposure request. Stack-Up has one confirmed live optical movement; repeated capture reliability and Gyromite movement still need confirmation.

## Resets and limits

Selecting a game or **Home** initializes that game's virtual pieces. **Emergency Stop** in live mode stops camera capture and clears the selected game; in the file preview it cancels its local animation. Game exit clears context and releases buttons. The RetroPie receiver also scans the running RetroArch process and resends game identity after a UNO Q restart. It does not infer Hector's position, gate animation, Stack-Up score, or game victory.

See [configuration](CONFIGURATION_REFERENCE.md), [network architecture](network-architecture.md), [optical input](optical-input.md), and the [verification report](UNATTENDED_TEST_REPORT_2026-09-24.md).
