# Optical game input: camera watching a modern display

## Primary approach

Mount a small adjustable camera with the UNO Q and aim it at the cabinet's LCD/OLED game display. R.O.B.'s eyes are drawn in the UI; there is no physical robot head. The camera watches the brightness changes when Gyromite or Stack-Up sends a command. UNO Q Linux converts the changes into one of the game's single-step virtual robot primitives. The camera stream supplies a small alignment preview in browser diagnostics. The exact ROM-derived messages and actions are in [ROM signal analysis](ROM_SIGNAL_ANALYSIS.md).

The original Nintendo design used a photo detector looking at a CRT. [Nintendo's photosensing patent](https://patents.google.com/patent/US4815733A/en) describes white/black image changes, a start/trigger structure, and updates aligned to vertical blanking. This supports the basic idea of optical decoding, but **does not prove that any particular camera and modern display combination will capture the pulses correctly**. The modern screen may show the flashes while its refresh behavior, scaling, image processing, pixel persistence, or brightness controls alter their timing. The camera can also miss or smear transitions through its frame rate, exposure, rolling shutter, or automatic gain.

## Processing pipeline

```text
camera frames + timestamps
  → locate game display / flashing region
  → lock a small region of interest
  → measure normalized brightness per frame
  → recover 13 dark/green bits at the game-frame clock
  → validate `000101w1x1y1z` and the selected game's command set
  → assign one event to one complete transmission
  → send one bounded primitive to the planner
```

Start with fixed camera placement and a user-adjustable rectangle on the browser dashboard. Automatic flash-region detection can come later. Bench-test delivered 60, 120, and 240 fps camera modes, short fixed exposure, fixed gain, and fixed white balance; the roughly 60 Hz game bit rate cannot be trusted from nominal camera frame rate alone. A 60 fps camera can decode idealized one-frame samples, but capture phase, exposure, display persistence, and dropped frames may lose transitions. At 30 fps, some one-frame bits cannot be distinguished from adjacent bits by this frame-sampling decoder. A higher delivered rate provides margin rather than a guaranteed result. Record actual frame timestamps. The decoder should expose raw brightness, threshold, bit timing, candidate bits, final command, confidence/rejection reason, and last-seen time so failures are understandable. A second region away from the game screen helps reject ambient flashes.

The ROMs show that Gyromite sends **two-level** up/down commands while Stack-Up sends **one-level** up/down commands. Both send one-station left/right and open/close. The ready-light command and alternating alignment-test flashes cause no arm movement. Repeated identical *separate* transmissions are valid game commands, especially during Stack-Up Memory playback; duplicate suppression applies only to overlapping detections of the same captured frames.

An accepted optical command is **not** a raw browser animation request. It goes through mode, virtual pose, object-state, and busy checks on the UNO Q. The system must show `NO SIGNAL`, `UNREADABLE SIGNAL`, or `COMMAND ACCEPTED` distinctly. A malformed or incomplete pulse train produces no virtual action.

The [original instruction manual transcript](https://www.atarihq.com/tsr/manuals/robmanual.txt) distinguishes a flickering test indication, a steady ready indication, and an unlit indicator during movement. It also notes that an overly bright screen can pass the test indication yet fail movement commands. For R.O.B. Vision, **flash visible**, **command decoded**, **ready to act**, and **busy moving** must be separate states backed by actual evidence. The historical 1–2 m CRT placement is a test candidate, not a camera specification; check the usable distance experimentally on the chosen LCD/OLED.

## Bench feasibility test before camera selection

1. Use the intended LCD/OLED, emulator/core, refresh setting, video filters, and actual game. Aim the candidate camera at the game's flash area from the planned robot position.
2. Record lossless or minimally compressed frames with monotonic timestamps. Capture the game's own test flash and every movement command many times, alongside idle gameplay. Include Gyromite's two-level movements and Stack-Up's one-level movements.
3. Plot the brightness trace and compare it with a fast reference light sensor if needed. Determine whether each pulse and gap remains distinguishable after display and camera sampling.
4. Verify complete 13-bit command identification against the [ROM-derived patterns](ROM_SIGNAL_ANALYSIS.md) across reasonable brightness, ambient light, viewing angle, and scaling settings. Check false triggers during ordinary gameplay and while R.O.B.'s own eye/display lights are active.
   Include glare, fluorescent lighting, volume/menu overlays, occlusion, exposure saturation, and a small shift of the camera or display. The original manual identifies these as reception risks; test their modern equivalents instead of assuming the camera behaves like its photosensor.
5. Aim for **at least 99 correct decodes in 100 repeated transmissions per command, with zero idle false triggers in a representative play session** before committing the camera to the mechanical design. This is a project acceptance target, not a claim of current performance.
6. Repeat after any camera, panel, video-mode, or emulator change. Keep sample recordings and decoder traces as reproducible test fixtures; do not put ROMs or copyrighted game footage in the public repository.

For Stack-Up, the [booklet](STACK_UP_MANUAL_NOTES.md) adds two specific captures: Memory playback at each offered speed, and Bingo when one key completes a row and column simultaneously. The latter is a documented no-command condition despite simultaneous flashing. The decoder and planner must make no move. A camera exposure that merges two flashes cannot be accepted as a valid single command.

If the candidate IMX219 camera cannot sample the relevant transitions reliably, evaluate a faster camera or a small reference photodiode beside it. The camera can still provide framing and the visual preview. The user-preferred camera path remains the first experiment; an emulator hook is a later fallback. Choose the final capture device from traces, not advertised resolution.

## Build implications

- Reserve one eye for a clear, stable camera aperture with adjustable focus/aim and a removable lens window. Keep decorative eye LEDs out of its optical path.
- The UNO Media Carrier is a candidate because Arduino documents MIPI-CSI camera inputs compatible with IMX219 modules. Physical cable routing must accommodate head rotation without excessive bending.
- The browser dashboard on laptop, iPad, or phone should make the virtual robot and accessories primary, with command, mission, and modeled pose visible. Camera alignment and flash traces belong in a diagnostic panel.
- The cabinet-to-robot network is used for sensed controller feedback and optional hooks; seeing the game flashes requires no incoming network command.

## References

- [Nintendo photosensing video game control patent](https://patents.google.com/patent/US4815733A/en) — original brightness-code mechanism and timing tied to CRT frames.
- [Arduino UNO Media Carrier](https://docs.arduino.cc/hardware/uno-media-carrier) — supported internal camera and display connector paths.
- [Original R.O.B. instruction manual transcript](https://www.atarihq.com/tsr/manuals/robmanual.txt) — historical setup, ready/busy indication, and optical troubleshooting; see [our design notes](HISTORICAL_MANUAL_NOTES.md).
