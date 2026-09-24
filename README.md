# R.O.B. Vision

R.O.B. Vision brings Nintendo's Robotic Operating Buddy to life as a **virtual robot**. The Arduino UNO Q is the planned controller. Its camera will watch Gyromite and Stack-Up flashes on a modern game display, animate R.O.B. and every accessory in a browser on a laptop, iPad, or phone, and send Gyromite's virtual Controller 2 buttons to the game host over Wi-Fi or Ethernet. No physical robot, motors, gyros, trays, or spinner will be built.

**Available now:** the interactive preview, a local controller service, ROM-derived optical decoder, optional OpenCV camera capture, shared virtual Stack-Up and Gyromite state, and a dashboard that follows that controller over HTTP. The camera path and Gyromite game-host button return have not been validated on hardware. The original preview remains available separately.

On the UNO Q, **R.O.B. Vision** is its own Arduino App Lab app, listed alongside VirtualGlove. Its App Lab entry uses the existing controller when it is already running, or starts it when needed. App Lab on this UNO Q starts only one app at a time, so VirtualGlove must be stopped in App Lab before starting R.O.B. Vision there. The independent R.O.B. Vision controller remains available at `http://arduiain.local:8766/dashboard/`; enter the controller token stored in the UNO Q's `~/.config/rob-vision/environment`. Refresh **My Apps** after installation if the new tile does not appear.

## Try the live controller

From this folder, run `python3 -m controller.service`. Open [the live dashboard](http://127.0.0.1:8766/dashboard/) and choose **Stack-Up** or **Gyromite**. The controls now send actions to the controller; reloading the page restores its current state. The Activity Feed distinguishes manual actions from decoded camera actions. **Home** resets the selected virtual game. **Emergency Stop** stops capture and clears the game session.

To use a camera, install the optional dependency with `python3 -m pip install -r requirements-camera.txt`, then select **Start Camera**. The capture code requests 120 fps and reports the delivered rate. Aim the camera at the game's flashing screen area; the default crop is the central 60% of the image. The small camera preview outlines the sampled region; `--camera-index 0 --camera-roi 0.2,0.2,0.6,0.6` can start capture with a chosen crop. OpenCV camera indexing and actual frame timing need to be checked on the intended UNO Q camera and display. A green/dark threshold and fixed 60 Hz cell period are initial bench settings, not calibrated game settings.

To serve a phone or iPad on a trusted LAN, set `ROB_VISION_TOKEN` and run `python3 -m controller.service --host 0.0.0.0`; open the controller's LAN address on the device and enter the token in the dashboard. Do not expose this service to the public Internet. The game host can notify the controller of a launch through `tools/notify_game.py`, which uses the exact ROM registry and leaves the game launch running if the controller is unavailable. The launch helper is not installed into RetroPie automatically.

**Play readiness:** Stack-Up's virtual pieces can already follow manual controller commands, and the service can consume camera frames when OpenCV and a compatible camera are present. Real optical play still requires calibration and timing validation on the target display. Gyromite's virtual pad states are modeled, but the game-host Controller 2 receiver and A/B mapping are not connected, so Gyromite cannot yet control the game.

Arduino documents [USB camera support on UNO Q](https://docs.arduino.cc/hardware/uno-q) through a powered USB-C dongle and [IMX219 camera inputs on the UNO Media Carrier](https://docs.arduino.cc/hardware/uno-media-carrier). The current capture adapter uses OpenCV's camera index; we still need to identify the UNO Q's actual device node and measure delivered frame timestamps before choosing either path.

## Try the preview

Open [the dashboard](dashboard/index.html), or serve this folder locally with `python3 -m http.server 8000` and visit `http://localhost:8000/dashboard/`.

Choose **Gyromite** and select **Run Demo Sequence**. The finite sequence demonstrates a single gate pressed with an unspun gyro, two spinning gyros on separate pads, one spin-down and re-spin recovery for each, and a final return to both holders. **Home** resets immediately. Stack-Up demonstrates red moving alone to Tray 4, followed by blue and white moving together to Tray 2. Its local command controls can move any valid disc group; **Home** restores all five to Tray 3. Pose Lab is a character-only movement sandbox. All graphics are original SVG/CSS drawn for this project; the current preview uses no game or hardware connection.

## How the finished system will work

1. The cabinet runs the game on an LCD or OLED screen. The UNO Q camera watches its optical command area.
2. A validated command changes the UNO Q's virtual R.O.B. pose and accessory model. The browser subscribes to that state and shows the action in real time.
3. In Gyromite, a virtual gyro or a held unspun gyro presses a virtual red or blue pad. The UNO Q sends the corresponding Controller 2 button state to the paired game host over LAN. When the virtual pad releases, the button releases.
4. In Stack-Up, commands move virtual discs among five trays. The game modes documented in the manual have no Gyromite-style tray-button return path.

The planned RetroPie launch hook identifies an exact configured game filename, following the VirtualGlove approach. The local [resolver](tools/identify_game.py) and [registry](config/games.json) already demonstrate name matching. A launch name supplies context; optical flashes remain the command source. User-supplied ROMs stay outside this repository.

## Guides

Start with the [documentation index](docs/INDEX.md), [user guide](docs/USER_GUIDE.md), [gameplay guide](docs/GAMEPLAY_GUIDE.md), and [virtual system contract](docs/VIRTUAL_SYSTEM.md). The [technical architecture](docs/TECHNICAL_ARCHITECTURE.md), [ROM signal analysis](docs/ROM_SIGNAL_ANALYSIS.md), and [verification plan](docs/VERIFICATION_PLAN.md) describe the planned integration.

Printable editions: [User Guide](output/pdf/R.O.B.-Vision-User-Guide.pdf), [Technical Reference](output/pdf/R.O.B.-Vision-Technical-Reference.pdf), and [Quick Reference](output/pdf/R.O.B.-Vision-Quick-Reference.pdf).

Historical Nintendo manuals and the Robert project inform behavior, but their text or code is not reused in this implementation. Game artwork and Nintendo marks remain with their owners.
