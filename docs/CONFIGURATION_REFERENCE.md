# R.O.B. Vision configuration reference

**Status:** Current code defaults and installed test-machine behavior as of 25 September 2026. Camera and display calibration remains open.

| Setting | Current value or location | Meaning |
| --- | --- | --- |
| App Lab gateway | HTTP port 80 | `http://arduiain.local/dashboard/` forwards to the controller. |
| Controller service | Port 8766 | Direct `/dashboard/` and `/api/` access. Local CLI binds loopback by default; use `--host 0.0.0.0` for a trusted LAN. |
| Controller token | `ROB_VISION_TOKEN` or UNO Q `~/.config/rob-vision/environment` | Required for RetroPie launch events, game-frame commands, and authenticated receiver polls, not LAN browser controls. Keep private. |
| Camera index | `0` for manual start | OpenCV probes physical capture devices and excludes codec-only UNO Q video nodes. The tested Kiyo Pro opens as `/dev/video2` on the UNO Q; device numbering may change. |
| Camera frame request | 60 fps | Delivered fps is measured and shown; a request does not guarantee that rate. |
| Kiyo Pro capture mode | `data/camera-mode`: absent or `mjpg480` | Default 640×480 MJPEG. `yuyv720` selects the 1280×720 uncompressed experiment. Recalibrate `data/camera-roi` when switching. The UNO Q is currently restored to `mjpg480`. |
| Camera region | `0.2,0.2,0.6,0.6` | Normalized x, y, width, height; central 60% of image. CLI `--camera-roi` can change it. |
| Optical threshold/cells | Luminance 0.38; fixed 60 Hz source cells | Initial decoder values derived from ROM analysis, not calibrated to the actual display. |
| Gyro spin lifetime | 55 seconds | Illustrative virtual lifetime. |
| Fast Gate hold | 60 seconds maximum | Each manual press automatically releases. Fast Gates are available only when Gyromite is selected and camera capture is stopped. |
| Browser state polling | 500 ms | `/api/state` snapshot; recent events capped at 30. |
| RetroPie receiver polling | 50 ms; request timeout 250 ms | Root uinput service reads the UNO Q state. |
| RetroPie stale release | 750 ms since last good response | Both virtual buttons release; game exit and missing RetroArch also release them. |
| RetroPie process scan | 250 ms | Identifies active RetroArch launch and can resync UNO Q game context after restart, throttled to two seconds. |
| RetroPie game-frame socket | `/run/rob-vision/frames.sock` | The FCEUmm proxy sends one classified bit per rendered NES frame. The receiver validates sender credentials, ROM identity, and complete 13-frame commands. |
| Game-frame indicator | Last matching receiver heartbeat within one second | `/api/state.input.frame_hook` is true; camera movement decoding pauses to avoid duplicate actions. |
| Receiver online indicator | Authenticated poll within three seconds | Otherwise Setup/Mission show RetroPie offline. |
| Game registry | `config/games.json` | Exact case-insensitive ROM basenames for Gyromite and Stack-Up, including configured ZIP, 7z, and NES names. |

## Local commands

```sh
python3 -m pip install -r requirements-camera.txt
python3 -m controller.service --host 127.0.0.1 --port 8766
python3 -m controller.service --camera-index 0 --camera-roi 0.2,0.2,0.6,0.6
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Gyromite (World).zip" ""
python3 tools/identify_game.py end
```

The camera dependency is optional for manual controls and RetroPie game-frame play. On the UNO Q App Lab installation, OpenCV and the Kiyo Pro are present; Gyromite and Stack-Up Test modes were recognized at about 60 fps. Live camera commands were intermittent. The RetroPie frame link has independently decoded Stack-Up CLOSE and DOWN and updated the virtual model. The optional standalone `deploy/rob-vision.service` must stay disabled while App Lab owns port 8766. App Lab runs one app at a time on this device.

The repository includes UNO Q camera recovery, shutdown, early-start, and network-status host units. They are **not installed or enabled** by App Lab. Existing Avahi provides `arduiain.local`; the R.O.B. Vision status timer is diagnostic and does not create the mDNS name. See [UNO Q host helpers](../deploy/uno-q/README.md).

Record camera model, mount, display/emulator settings, measured fps, exposure, ROI, Test-mode behavior, and decoded-command results before changing these defaults for real optical play.
