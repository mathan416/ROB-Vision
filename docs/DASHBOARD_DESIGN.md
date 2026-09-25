# Laptop, tablet, and phone dashboard

**Status: design contract plus local simulation.** R.O.B. and all accessories are virtual. The current browser preview does not connect to the UNO Q camera service or game host.

## Visual hierarchy

The main pleasure of this interface is watching virtual R.O.B. act on visible game pieces. Robot motion, the held object, and the accessory station should read as one continuous event. The game screen and camera image support that event; the robot and pieces remain the main view. The live implementation should animate accepted optical commands from the UNO Q's virtual state and keep piece occupancy consistent with the same state used for Gyromite button output. Cosmetic eye and gyro effects may add personality, but must stay distinct from validated game input.

1. **R.O.B. model is the main view.** Keep the friendly face while drawing two outward-bent hand tips that converge around one object. Each hand is attached to one arm; neither hand contains its own little pincer. The shoulder hubs remain visibly connected to a shared carriage while the hands rise/lower and sweep left/right. Turn the head in the same direction as the sweep. Place the hands visually in front of the prop so the contact is readable. Animate body station, vertical level, shared grip state, and current/next action. Show when a pose comes from a scripted preview or a validated optical command.
2. **Game table is always visible in the selected mode.** Gyromite shows spinner, two gyro docks, red/blue button trays, and both gyros. Stack-Up shows five numbered trays and five colored blocks, including the mode-specific starting stack. Show modeled object location, virtual pad state, and whether each update came from a scripted preview or a validated command.
3. **Status and activity remain legible.** Show game identity source, optical decode, accepted/rejected primitive, busy state, virtual pose, virtual pad state, and Gyromite receiver freshness. A decoded command, a virtual action, and a game-host acknowledgement are different events.
4. **Camera video is secondary and optional.** A small tile may show a downsampled view of the game display for orientation. It cannot prove an optical command. If unavailable, the tile says so and the rest of the dashboard still works.
5. **Detailed camera analysis belongs in diagnostics.** The UNO Q camera watches the cabinet display. Show its region of interest, brightness trace, and frame timing on demand. Keeping the detailed feed off the main screen leaves R.O.B. and the pieces as the focus.

## Device layout

The UNO Q should serve the same browser application and state stream over the trusted LAN to a laptop, iPad, or phone. Desktop and wide tablet layouts can keep the R.O.B. model beside mission and telemetry cards. A phone stacks the model, game table, status, and controls vertically, with touch-sized controls and no horizontal scrolling. The observer tile never displaces the model or hides a fault. Reconnection should request a fresh state snapshot and show data age; it must not replay movement commands.

The current static preview has been checked in a browser at 390 px and 820 px widths. Device touch behavior, real LAN latency, and observer-video bandwidth remain untested.

## Proposed live event contract

The UNO Q, not the browser, owns the game session and virtual robot state. Publish a versioned snapshot on connection, then ordered events with session ID, monotonic sequence, timestamp, and freshness. Include game/mode, optical decode and rejection reason, accepted primitive, virtual pose/grip, gyro or block locations, virtual pad states, RetroPie receiver status, and faults. Browser clients render this stream and can reconnect without changing game state. Optional operator controls send bounded intents through the same virtual controller.

The local controller now offers a small, low-rate JPEG camera preview with the sampled region outlined. It is a framing aid in the secondary Game Camera tile. The command decoder consumes original timestamped frames locally, never the browser preview, so a missing or hidden preview does not interrupt optical decoding or motion. The preview is not recorded by default and requires the controller token on a LAN deployment.

## Current preview boundary

The finite Gyromite demo first shows R.O.B. holding an unspun gyro on one virtual pad, then runs a two-gyro spin relay. Each gyro has an illustrative 55-second spin-down clock, tips, and releases its virtual pad. R.O.B. re-spins each once, waits for both to stop again, returns them to their holders, and ends in a stable COMPLETE state. Both speed bars and red/blue virtual button states remain visible. HOME, mode change, demo restart, and simulation stop cancel pending actions. The UNO Q will own these virtual states during connected play; no physical tray contact is involved.

The [dashboard](../dashboard/index.html) animates R.O.B. and his virtual accessories together. Gyromite shows two matching gyros, two holders, the right-side spinner, and the red/blue button pads. Its finite demo ends with both gyros stored. Stack-Up shows five trays and all five blocks. Its command-by-command demo moves red from Tray 3 to Tray 4, then grips blue and white together and places both on Tray 2. The Live Model, Accessory Bay, and Game Table all read the same virtual stack state. Local Stack-Up controls apply the same one-level and one-station actions and reject blocked moves without changing the blocks. The art uses a three-quarter perspective, not measured hardware trajectories. Camera-driven play is still pending.

Pose Lab is a character-only motion sandbox. It shows no gyro, block, or game fixture. Its short greeting and the manual Pose Preview controls let the viewer inspect turns, arm height, and the shared hand grip without claiming an optical command. The sidebar uses a R.O.B. portrait in this mode, and the game-table area explains that there are no game pieces. The [ROM signal table](ROM_SIGNAL_ANALYSIS.md) and [technical architecture](TECHNICAL_ARCHITECTURE.md) specify how connected play will drive visual state.

The original [Gyromite manual](https://www.digitpress.com/library/manuals/nes/gyromite.txt) describes opening and closing the arms, raising/lowering, and turning/carrying. The user-provided [R.O.B. photo reference](https://www.ssbwiki.com/R.O.B.) and [physical demonstration](https://www.youtube.com/watch?v=d2ezDBhkEOs) inform the silhouette and station presentation. The visual design keeps the current expressive face; its station paths are virtual art choices, not measured hardware trajectories.
