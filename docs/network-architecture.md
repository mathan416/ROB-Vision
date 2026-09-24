# R.O.B. Vision network architecture

R.O.B. is a virtual model owned by the Arduino UNO Q. The cabinet displays the game; the UNO Q camera watches the optical flashes. A laptop, iPad, or phone receives the UNO Q's state and renders R.O.B. and every accessory. There is no physical robot or tray sensor and no USB data tether to the cabinet.

```text
cabinet game display ── optical flashes ──> UNO Q camera/decoder
                                               ↓
                                     virtual R.O.B. controller
                                         ↙           ↘
                       state/events to browsers     Gyromite pad buttons
                              over LAN              over paired LAN link
                                                          ↓
                                             game-host Controller 2 receiver
```

The optional RetroPie start/end hook sends exact configured game identity to the UNO Q. It selects a mode but is not a movement command. The optical decoder supplies movement commands. If camera capture proves infeasible, a future emulator adapter may supply equivalent validated commands through an authenticated channel; that fallback is not implemented.

## Gyromite return path

The UNO Q derives red/blue virtual pad states from its virtual gyro and hand model. A spinning upright gyro on a pad presses it; an unspun gyro explicitly held down by R.O.B. also presses it. Moving or tipping it releases it. These short-lived states are sent to a paired receiver that exposes a virtual second controller to the emulator. The original booklet does not establish the red/blue-to-A/B mapping clearly enough to hard-code it; measure the mapping in a running game.

Packets need a session identifier, monotonic sequence, version, authentication, both current button states, and a bounded freshness period. The receiver releases both buttons on timeout, unpairing, game exit, or invalid input. A local socket send is not evidence that the emulator accepted a button; receiver status belongs in the dashboard. Network reconnection does not replay an old held state without a new fresh snapshot.

Stack-Up's documented modes do not use this Gyromite tray-button return path. Its virtual piece state still streams to browser clients.

## Browser stream and privacy

Browsers subscribe to a versioned snapshot followed by ordered events. The UNO Q remains authoritative if a tab closes or reloads. The main view shows R.O.B., virtual pieces, commands, and controller-link freshness. The game-screen camera image is used for calibration diagnostics, while the main view remains the robot. Limit any camera stream to paired/trusted clients and avoid recording ROM images by default.

Wi-Fi is the intended baseline. A compatible Ethernet adapter is optional; verify UNO Q power and interface support on the actual board. The application protocol should behave the same over either link. The local dashboard presently has no network service or game receiver.
