# R.O.B. Vision parts plan

The build is an electronic controller with a virtual R.O.B. display. Historical gyros, spinner, pads, trays, arms, and blocks are software models, not parts to buy.

| Item | Current status |
| --- | --- |
| Arduino UNO Q | In use for App Lab controller, HTTP panel, virtual state, and LED matrix sketch. |
| RetroPie game host | `retropie.local` has launch hooks and a paired virtual Controller 2; both Gyromite gate colors have responded. |
| Camera and adjustable mount | Optional for RetroPie frame-link play; the attached Kiyo Pro provides preview and Test checks. Camera-only movement remains experimental. |
| UNO Q power and enclosure | Use adequate supply and ventilation; final mount depends on the chosen camera. |
| Wi-Fi or Ethernet adapter | Current setup uses an Ethernet adapter on a USB hub; Wi-Fi uses the same app protocol. |
| Laptop, tablet, or phone | Main browser display for R.O.B. and game accessories. |

No servo, motor driver, home switch, physical gyro, tray sensor, spinner motor, or actuator supply belongs to this project. Do not assume a 60 fps camera will capture every one-frame game flash; validate before fixing a mount.
