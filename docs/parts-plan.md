# R.O.B. Vision parts plan

The build is an electronic controller with a virtual R.O.B. display. The historical gyros, spinner, pads, trays, arms, and blocks are **software models**, not parts to purchase or fabricate.

| Item | Purpose | Status |
| --- | --- | --- |
| Arduino UNO Q | Run camera capture, optical decoding, virtual robot state, dashboard service, and Gyromite LAN sender | Candidate controller; runtime integration unimplemented. |
| Compatible camera and mount | Watch the game's optical flash area on LCD/OLED | Interface, exposure, focus, and frame timing require bench proof. |
| UNO Q power supply and ventilated enclosure | Stable controller operation | Select after confirming board and camera current requirements. |
| Wi-Fi or compatible Ethernet adapter | Link UNO Q, dashboard devices, and game host | Wi-Fi baseline; Ethernet optional. |
| Laptop, iPad, or phone | Main animated R.O.B. display | Existing browser preview available. |
| Game host with virtual Controller 2 receiver | Accept Gyromite red/blue button states | Proposed software; no live receiver yet. |
| Optional observer camera | Contextual image separate from the game-screen camera | Not required. |

No servo, motor driver, home switch, gripper, physical gyro, tray sensor, spinner motor, or actuator supply is part of the current scope. Validate exact UNO Q camera and network compatibility before finalizing purchases.
