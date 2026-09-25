# R.O.B. Vision changelog

## UNO Q network status counterpart — 24 September 2026

- Added R.O.B. Vision versions of the VirtualGlove host Wi-Fi status sampler, service, and timer. They publish physical Wi-Fi/Ethernet link health and broadcast addresses without network names or credentials.
- Verified the sampler once on the UNO Q and validated the service and timer with systemd. The existing Avahi daemon already provides `arduiain.local`; no mDNS configuration was replaced.

## UNO Q host helper counterparts — 24 September 2026

- Added R.O.B. Vision versions of the VirtualGlove camera recovery, shutdown, and early-start host files, plus the companion early-start script. Paths, markers, enrollment, and service names are project-specific.
- Kept the network-hub safeguard for the camera recovery helper: when camera-port power cycling is unavailable, it refuses to reset a hub that carries Ethernet. Added isolated tests for enrollment, that refusal, and a supported camera-port cycle.
- Documented that the host helpers are not yet installed or wired into the Setup page's camera reconnect action.

## Unattended two-game verification — 24 September 2026

- Added independent optical-command-to-model flow tests for Gyromite and Stack-Up, including pad release, grouped block transfer, collision rejection, and game-specific command isolation.
- Made the RetroPie receiver recover the active game after a UNO Q restart by reading the exact RetroPie RetroArch launch and replaying the authenticated launch event. Verified recovery against a live Gyromite session; virtual buttons remain released when no matching Gyromite process is active.
- Booted the supplied Stack-Up ROM in a displayless RetroArch smoke test and confirmed the supplied ZIP ROM hashes match the documented command tables. See the [unattended test report](UNATTENDED_TEST_REPORT_2026-09-24.md) for evidence and remaining camera/display limits.

## UNO Q matrix display — 24 September 2026

- Added an App Lab microcontroller sketch for the built-in 13×8 blue matrix: startup hourglass, idle eyes, Gyromite and Stack-Up title marks with animated eyes, Test `T`, pairing `P`, and fault `X`.
- Added a Linux Router Bridge sender driven by the controller's game, camera, Test, and accepted-action state. A heartbeat returns the sketch to the hourglass if the Linux side disappears.
- The physical sketch compiled and uploaded on the UNO Q and the bridge endpoint responded. Direct visual confirmation of each matrix animation remains pending.

## Setup and live controls — 24 September 2026

- Added a Setup page with certificate-pinned one-time RetroPie pairing, receiver status, camera alignment preview, game Test mode ready-light acknowledgement, Gyromite Fast Gates, and six Stack-Up command checks.
- Moved the Game Table beside Pose Preview and System Vitals, and removed the secondary camera tile from Mission Control.
- Verified both Gyromite gate colors during live Game A play. UNO Q camera capture remains unverified until a camera is attached.

## Local controller and camera path — 24 September 2026

- Moved Pose Preview above System Vitals and made its live controls send commands to an authoritative Python controller service.
- Added ROM-pattern optical decoding, optional OpenCV camera capture with measured fps, exact-name launch notification, and shared Stack-Up/Gyromite virtual state.
- Added a live dashboard at port 8766 while retaining the static scripted preview. Camera and button-return hardware remain to be validated.
- Added synthetic decoder/model tests and updated the user and technical guides.

## Stack-Up grouped carries — 24 September 2026

- Added a browser virtual Stack-Up controller with five ordered tray stacks, six height levels, five stations, open/closed hands, and an ordered carried block segment. Invalid moves leave the model unchanged.
- Updated the demo to transfer red alone, then blue and white together. Live Model, Accessory Bay, and Game Table now render the same changing block state.
- Made the Stack-Up command buttons interactive in local simulation and added five model tests for grouped carries, conservation, bounds, and blocked moves.
- Renamed Free Play to Pose Lab and removed its stray gyro artwork; it remains a character-only motion sandbox.

## Virtual robot scope and finite Gyromite demo — 24 September 2026

- Confirmed the UNO Q will own a virtual R.O.B. and accessory state; no physical robot or game pieces are planned. Earlier physical-build entries below are historical and superseded.
- Added an unspun held one-gate press, independent gyro spin-down, one re-spin recovery per gyro, and final return to both holders. The scripted demo now stops.
- Reworked the user, system, network, setup, and verification guides around the virtual controller and its Gyromite LAN button return path.

## Display direction update — 24 September 2026

- Made a responsive browser dashboard on laptop, iPad, or phone the primary display, replacing the planned base-mounted panel.
- Added a game-table illustration for both accessory sets and a small placeholder for an optional camera facing the physical robot. The head camera remains dedicated to game-screen flashes and alignment diagnostics.
- Updated hardware, network, player, and verification guides for this display arrangement. The preview is still simulated; no live video or telemetry is connected.

## Design preview 0.1 — 24 September 2026

- Created the original interactive dashboard simulation with three accessory modes, direct controls, activity feed, and simulated stop/reset.
- Chose a close R.O.B. silhouette; the initial base-display idea was superseded by the browser dashboard above.
- Defined the UNO Q Linux/MCU split and Wi-Fi/Ethernet cabinet connection.
- Made a head camera watching Gyromite and Stack-Up flashes on a modern LCD/OLED the primary game input; emulator hooks remain optional.
- Defined sensor-confirmed tray feedback to a RetroPie virtual second controller.
- Added design-stage user, gameplay, installation, hardware, technical, configuration, troubleshooting, verification, safety, rights, and quick-reference guides.
- Incorporated the original R.O.B. instruction manual as a cited historical reference for optical test/ready/busy behavior, setup hazards, and modern display acceptance tests.
- Incorporated the Gyromite instruction booklet as a cited reference for Direct/Game A/Game B flow, two-gyro play, fixture roles, and tray/button mapping tests.
- Incorporated the Stack-Up instruction booklet scan as a cited reference for five numbered trays, ring-shaped pieces, Direct/Memory/Bingo modes, Memory timing, and Bingo's ambiguous simultaneous-command case.
- Added a local, exact-filename Gyromite/Stack-Up launch resolver and registry for the supplied `.zip`, `.7z`, and `.nes` names, plus tests and a planned RetroPie start/end notification contract. No hook or network receiver is installed.

No physical robot, camera decoder, network receiver, ROM interface, or installer is included in this version.
