# R.O.B. Vision: virtual system contract

**Current scope:** R.O.B. is a character and accessory simulation rendered in the browser. The Arduino UNO Q is the intended controller: its camera watches Gyromite or Stack-Up on the cabinet screen, its software decodes the optical commands, updates the virtual R.O.B. and pieces, and sends virtual Controller 2 button states to the game host over Wi-Fi or Ethernet for Gyromite. A laptop, iPad, or phone shows the dashboard. There is no physical robot, moving arm, gyro, tray, spinner, or tray sensor to build.

**Available now:** the browser contains scripted demonstrations and can also follow a local Python controller service. That service decodes the ROM-derived light patterns from timestamped samples, optionally captures frames through OpenCV, applies Stack-Up and Gyromite virtual commands, and serves the authoritative state to browser clients. Stack-Up preserves all five discs and grouped carries. The camera path has only synthetic timing tests so far; it has not been validated with the intended UNO Q, display, or emulator. Gyromite's Controller 2 return path is still absent.

## Runtime responsibilities

| Component | Responsibility |
| --- | --- |
| Cabinet display and emulator | Render the original game's optical flashes and accept ordinary controller input. |
| UNO Q camera service (planned) | Capture a timestamped region of the cabinet display; decode a complete optical command or reject it. |
| UNO Q virtual robot controller (planned) | Apply one validated command to a bounded virtual pose, two gyro states, or five Stack-Up discs; publish ordered state events. |
| Gyromite return path (planned) | Send the controller's virtual red/blue pad state over LAN to a paired virtual Controller 2 receiver; release on disconnect, exit, or stale messages. |
| Browser dashboard | Render the robot, accessories, game pieces, controls, status, and event history from the UNO Q's state stream. Multiple screens observe the same session. |
| Optional RetroPie launch hook | Supply an exact, configured game identity on launch/exit; it does not replace optical command decoding. |

The controller service owns live game state. The browser does not independently decide what command was seen or which game button is pressed. The dashboard's separate static preview still runs its own local script. Deploying the service on the UNO Q remains a hardware validation task.

## Gyromite virtual rules

Each gyro has a location (`holder`, `held`, `spinner`, `red_pad`, or `blue_pad`) and spin phase (`idle`, `accelerating`, `spinning`, `wobbling`, or `stopped`). The controller tracks Gyro A and Gyro B separately. A virtual pad is pressed when a spinning gyro is upright on it, or when R.O.B. is explicitly holding an unspun gyro down on that pad. Lifting, moving, or tipping the gyro releases the pad. The button state is derived from this virtual model and sent over LAN; there is no physical contact sensor. The demo uses a 55-second illustrative spin lifetime. Actual play timing will be tuned for fun and compatibility rather than presented as a measured property of Nintendo hardware.

The [Gyromite booklet](https://www.digitpress.com/library/manuals/nes/gyromite.txt) says one gate can be moved without spinning a gyro. For two gates, spinning one gyro lets it keep the first pad pressed while R.O.B. moves the other. When a gyro is no longer needed, R.O.B. returns it to its holder. A completed action must update both the visible object and the virtual controller state together. Loss of the LAN return path releases both game buttons even if the local animation remains visible.

The finite preview demonstrates one unspun held press, a two-gyro spin relay, one recovery per gyro after spin-down, then a return of both stopped gyros to their holders. It ends in a stable `COMPLETE` state. Future live game play should follow optical/player commands; the scripted preview is not an autonomous strategy for solving a level.

## Stack-Up virtual rules

Track five colored discs, their order, five tray stacks, the arm station (1–5), height (six levels), and the gripper state. Closing the hands at a disc level can grip that disc **and every disc above it** as one carried stack segment. Opening releases the whole carried segment onto the target tray in the same order. Reject a grip with no disc at that level, a blocked turn, an out-of-range move, or a placement that would exceed the tray's five-disc capacity. A decoded flash carries one movement command, not a disc ID, destination, target pattern, or score. Stack-Up does not need Gyromite's virtual Controller 2 pad return path in the documented modes. The dashboard must show the modeled stack and distinguish a received game command from the resulting inferred piece movement.

## Failure boundaries

- A partial or ambiguous optical flash never produces movement.
- Unknown game identity or mode does not select a game-specific controller mapping.
- One virtual action completes before another begins unless a game mode's measured timing demands a bounded queue.
- Game exit, network timeout, restart, or a simulation stop releases both virtual Gyromite buttons.
- Browser reconnect receives a fresh snapshot and ordered events; it never restarts a partially completed action on its own.
- The original game sees only controller input. Unless an optional emulator hook is later implemented, the virtual controller cannot claim to know the professor's location, gate animation, or level outcome.
