# R.O.B. Vision configuration reference

**Status: prototype settings plus proposed hardware calibration.** The static preview uses browser memory; the live Python controller serves shared state. Camera ROI, requested frame rate, and light threshold are initial code settings. No UNO Q settings service, pairing store, or Gyromite game receiver exists yet.

| Area | Planned settings | Validation |
| --- | --- | --- |
| Optical capture | Camera identity, exposure, gain, frame mode, flash region, timing thresholds | Stable timestamps and complete Test-mode command on the actual display. |
| Game identity | Exact configured ROM basenames and game IDs | No substring guessing; unknown title and exit clear context. |
| Virtual robot | Pose bounds, action duration, hand/grip rules, object locations | No impossible transfer or overlapping actions. |
| Gyromite | Gyro spin lifetime, wobble threshold, initial holders, pad rules, red/blue Controller 2 mapping | One held unspun press, two-gyro relay, independent release, measured A/B game response. |
| Stack-Up | Tray indices, starting disc order, six height levels, mode timing | Ordered disc groups move together when gripped below the top; no command loss in Memory mode. |
| LAN | UNO Q and game-host identities, receiver address, pairing key, packet interval, timeout | Fresh authenticated state only; both buttons released on timeout/exit. |
| Dashboard | Text scale, reduced motion, camera diagnostic visibility | Touch and keyboard use on laptop, iPad, and phone. |

Optical calibration records should include display and emulator mode, camera/mount, exposure, frame timing trace, ROI, date, and pass/fail result. Changing the display, camera mode, or video filter invalidates that calibration. Virtual gyro timing is a gameplay setting and must be identified as simulated; it is not a physical sensor threshold.

The only available local commands today are the browser preview and filename resolver:

```sh
python3 -m http.server 8000
python3 tools/identify_game.py start nes lr-fceumm "/roms/nes/Gyromite (World).zip" ""
python3 tools/identify_game.py end
```

The local camera trial uses OpenCV camera index 0, requests 120 fps, and samples the central 60% of the frame. Those are defaults for testing, not validated UNO Q settings. The service reports delivered fps and camera errors. There are no working game receiver or pairing commands yet.
