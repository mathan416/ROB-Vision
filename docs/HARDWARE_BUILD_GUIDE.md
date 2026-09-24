# R.O.B. Vision UNO Q hardware setup

**Scope:** build the small camera and network controller, not a physical R.O.B. R.O.B., hands, gyros, spinner, pads, and Stack-Up trays are virtual graphics and controller state. No motors, mechanical fixtures, tray sensors, motor drivers, or actuator power supply are required.

## Planned controller assembly

- Arduino UNO Q with a supported supply and enclosure that allows ventilation and service access.
- Compatible camera and mount aimed at the cabinet's LCD/OLED flash area. Confirm the camera interface, frame mode, focus, exposure control, and cable length on the actual UNO Q before ordering a fixed enclosure.
- Built-in Wi-Fi as the baseline LAN path, or a compatible Ethernet adapter if wired service is preferred. The cabinet and UNO Q share a trusted local network; no USB tether to the cabinet is planned.
- A laptop, iPad, or phone opens the dashboard from the UNO Q over LAN. It is the principal R.O.B. display. An optional observer camera could show the room or controller, but it is not required for the virtual robot.

## Commissioning order

1. Power the UNO Q and confirm the intended operating system, camera, and network interfaces independently.
2. Aim the camera at the game display. Fix focus and exposure, then record timestamped bright/dark traces while using the game's Test mode.
3. Validate optical framing and command decoding against both supplied ROM analyses before connecting any game return path.
4. Serve the dashboard from the UNO Q and verify the same virtual snapshot appears on laptop, iPad, and phone.
5. Pair the Gyromite LAN sender with the game-host receiver. Confirm red/blue virtual pad transitions, the actual A/B mapping, and release on disconnect or timeout.
6. Run full Gyromite and Stack-Up sessions and retain logs for failures. Do not treat the current browser demo as evidence that this integration is complete.

Cable routing and enclosure design should avoid blocking the camera view, heat vents, or wireless antennas. There is no moving R.O.B. mechanism to calibrate or guard.
