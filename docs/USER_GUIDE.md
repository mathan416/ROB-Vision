# R.O.B. Vision user guide

**Status: the UNO Q dashboard and RetroPie Gyromite Controller 2 link are running; camera capture on the UNO Q still needs hardware testing.** R.O.B. is a virtual character and accessory model. The robot, gyros, trays, spinner, and Stack-Up discs are drawn in the browser; they are not physical objects.

## Try the available preview

Open [the dashboard](../dashboard/index.html), or serve the project folder locally and open `/dashboard/` in a browser. The preview requires no UNO Q, ROM, camera, or network connection. It works on a laptop, iPad, or phone.

The large **Live Model** shows R.O.B. moving two opposing hands around one piece. **Accessory Bay** selects Gyromite, Stack-Up, or Pose Lab. **Game Table** gives a second view of the virtual pieces. **System Vitals** shows virtual pose, gyro spin, and virtual red/blue button state. The smaller game-camera tile is a placeholder. `SIMULATION` and `GAME LINK OFFLINE` mean no game is being controlled.

### Run Gyromite

1. Select **Gyromite**, then **Run Demo Sequence**.
2. First, watch R.O.B. hold an unspun gyro on the red pad. The virtual red button stays pressed only while he holds it there.
3. Then watch R.O.B. spin Gyro A and B and put them on the red and blue pads. Each gyro has its own illustrative spin-down clock.
4. When each gyro tips, its virtual button releases. R.O.B. re-spins each once. After both stop again, he returns them to their holders and the demo ends.

The 55-second spin time is a demonstration setting, not a historical measurement. Select **Home** to reset at any point, or **Run Demo Sequence** to start again. No player needs to reposition virtual pieces.

### Run Stack-Up or Pose Lab

**Stack-Up** starts with five colored discs on Tray 3. The demo moves red alone to Tray 4, then carries blue and white together to Tray 2, and stops. Use **Stack-Up Commands** below the view to try one virtual movement at a time; the grip button switches between **Close Hands** and **Open Hands**. R.O.B. can lift a disc together with every disc above it. **Home** restores all five discs to Tray 3. **Pose Lab** shows R.O.B. alone: its demo is a short greeting, and the **Pose Preview** buttons let you try turning, lifting, and gripping. It uses no game pieces or optical commands. **Emergency Stop** cancels the local sequence until **Reset Stop** is selected. It is a demo control, not a physical safety switch.

## Play with RetroPie

Open `http://arduiain.local/dashboard/` on a laptop, phone, or tablet and enter the controller token if prompted. Launch Gyromite on RetroPie; its launch hook selects Gyromite in R.O.B. Vision. **Fast Gates** appears above System Vitals. Select **Lower Blue** or **Lower Red** to press a gate immediately; select the same button again to raise it. **Release Both** raises both at once. Keyboard shortcuts are **2** for blue, **1** for red, and **0** to release both. Keep the dashboard open while playing. Each press releases automatically after 60 seconds, and game exit releases both. These controls let a player test gates without waiting for R.O.B.'s movement sequence. R.O.B. and the virtual gyros update in the display. The blue gate response was observed in Game A; the red gate still needs a separate visual check.

Fast Gates is available during Gyromite while camera capture is stopped. If you use the regular movement controls first, select **Home** to return gyros to their holders before using Fast Gates. It is a direct manual play control; optical command decoding remains separate.

## Camera game connection

The cabinet displays Gyromite or Stack-Up on a modern screen. The Uno Q camera will read the game's flashes and validate a complete command before the Uno Q changes the virtual R.O.B. state. A laptop, iPad, or phone will display that state over the LAN. An optional RetroPie launch hook can identify the configured ROM by exact filename; it will not replace flash decoding.

For Gyromite, the UNO Q will send red/blue virtual pad states to a paired virtual Controller 2 receiver over Wi-Fi or Ethernet. A spinning gyro upright on a pad presses it, as does an unspun gyro held there by R.O.B. Moving or tipping the gyro releases it. The game itself sees only Controller 2 input; without an optional emulator hook, R.O.B. Vision cannot know the professor's exact position or prove a gate's on-screen response. Stack-Up's documented modes do not use this tray-button feedback.

For a local controller trial, run `python3 -m controller.service` from the project folder and open `http://127.0.0.1:8766/dashboard/`. Choose a game; commands above System Vitals go to the controller and survive page reloads. Install `requirements-camera.txt` to enable **Start Camera**. Camera speed and screen decoding still need validation with the intended hardware. See the [virtual system contract](VIRTUAL_SYSTEM.md), [gameplay guide](GAMEPLAY_GUIDE.md), and [technical architecture](TECHNICAL_ARCHITECTURE.md).
