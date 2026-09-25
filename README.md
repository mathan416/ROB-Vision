# R.O.B. Vision

R.O.B. Vision brings Nintendo's Robotic Operating Buddy to life as a **virtual robot**. The Arduino UNO Q runs the controller. The RetroPie game-frame link reads Gyromite and Stack-Up commands at the emulator's frame rate; its optional camera can watch the display for alignment and Test-mode checks. R.O.B. and every accessory animate in a browser on a laptop, iPad, or phone, while Gyromite's virtual Controller 2 buttons return to the game host over Wi-Fi or Ethernet. No physical robot, motors, gyros, trays, or spinner will be built.

**Available now:** the interactive preview, UNO Q controller service, ROM-derived optical decoder, optional OpenCV camera capture, shared virtual Stack-Up and Gyromite state, and a dashboard that follows that controller over HTTP. A real RetroPie Gyromite launch/exit selected and cleared the UNO Q game. Red and blue pad press/release reached the test machine's virtual Controller 2, and the player confirmed both matching gate colors respond in Game A. The attached camera recognized both games' Test modes, and the new RetroPie frame link decoded all six movement/grip commands in each game during live Direct play. The original preview remains available separately.

On the UNO Q, **R.O.B. Vision** is its own Arduino App Lab app, listed alongside VirtualGlove. Start it from **My Apps**, then open `http://arduiain.local` on a laptop, phone, or tablet. The direct `http://arduiain.local:8766/dashboard/` address also works; both use the same controller and game state. The browser pages open directly without a controller-token prompt. The token stored in the UNO Q's `~/.config/rob-vision/environment` is used for the RetroPie receiver and launch hooks. App Lab on this UNO Q starts only one app at a time, so VirtualGlove must be stopped before starting R.O.B. Vision. Refresh **My Apps** after installation if the new tile does not appear. Do not enable the separate `rob-vision.service` while running the App Lab app because both would claim port 8766.

The built-in [Help center](dashboard/help.html) covers setup, both games, controls, status signals, and troubleshooting. The [Setup page](dashboard/setup.html) provides RetroPie pairing, camera alignment, Test mode ready-light acknowledgement, Gyromite red/blue pad checks, and Stack-Up command checks. The Mission page keeps the live robot, Fast Gates, and a Game Table beside Pose Preview and System Vitals. See the [Setup guide](docs/SETUP_GUIDE.md).

## Try the live controller

From this folder, run `python3 -m controller.service`. Open [the live dashboard](http://127.0.0.1:8766/dashboard/) and choose **Stack-Up** or **Gyromite**. The controls now send actions to the controller; reloading the page restores its current state. The Activity Feed distinguishes manual actions from decoded game-frame and camera actions. **Home** resets the selected virtual game. **Emergency Stop** stops capture and clears the game session.

To use a camera, install the optional dependency with `python3 -m pip install -r requirements-camera.txt`, then use **Start Camera Check** on Setup. Capture requests 60 fps and reports delivered frames over a four-second window. An identified Razer Kiyo Pro receives a temporary HDR-off and 1 ms manual exposure setting, then opens as 640×480 MJPEG. This reached about 60 delivered fps on the UNO Q on September 25, 2026; other cameras keep the general OpenCV path. Aim the camera at the game's flashing screen area; the default crop is the central 60% of the image. The Setup preview outlines the sampled region. For an App Lab camera position, save normalized `x,y,width,height` coordinates in the app's `data/camera-roi` file (or set `ROB_VISION_CAMERA_ROI`) and restart the app. **Start Camera Check** and **Reset & Reconnect** then use that region. After the camera was moved closer and straight-on, the test device uses `0.205,0.15,0.04,0.05` on a dark area of the game screen. The CLI also accepts `--camera-index 0 --camera-roi 0.2,0.2,0.6,0.6`. Stack-Up RIGHT and DOWN each moved the virtual R.O.B. in separate live optical tests, but later flashes were lost to 60 fps camera sampling; the RetroPie game-frame link now supplies exact commands without relying on camera timing.

To serve a phone or iPad on a trusted LAN, set `ROB_VISION_TOKEN` and run `python3 -m controller.service --host 0.0.0.0`; open the controller's LAN address on the device. The token is still required for the game-host launch hook and receiver identity, while browser controls are available to devices on that LAN. Do not expose this service to the public Internet. The game host can notify the controller of a launch through `tools/notify_game.py`, which uses the exact ROM registry and leaves the game launch running if the controller is unavailable. The dedicated `retropie.local` test machine has the launch and exit hooks installed; see [RetroPie setup](deploy/retropie/README.md).

**Play readiness:** Both games sent all six command types through the live RetroPie frame link and moved the virtual model where the move was valid. The camera recognized both Test modes, while camera-only movement remains experimental. See the [frame-link verification](docs/FRAME_LINK_TEST_2026-09-25.md) and [camera test report](docs/LIVE_OPTICAL_TEST_2026-09-25.md). Gyromite's virtual Controller 2 receiver is installed on `retropie.local`; the player confirmed that both red and blue gate controls work in Game A with the corrected mapping.

For responsive manual Gyromite play, use **Fast Gates** on `http://arduiain.local/dashboard/`: tap **Lower Blue** or **Lower Red** to press immediately, tap again to release, or choose **Release Both**. Keyboard shortcuts are **2**, **1**, and **0** respectively. Presses release automatically after 60 seconds. This works while camera capture is stopped and does not wait for R.O.B.'s movement animation.

Arduino documents [USB camera support on UNO Q](https://docs.arduino.cc/hardware/uno-q) through a powered USB-C dongle and [IMX219 camera inputs on the UNO Media Carrier](https://docs.arduino.cc/hardware/uno-media-carrier). The current capture adapter uses OpenCV's camera index; the attached Kiyo Pro is `/dev/video2` on this UNO Q and delivered about 60 fps in the live test.

## Try the preview

Open [the dashboard](dashboard/index.html), or serve this folder locally with `python3 -m http.server 8000` and visit `http://localhost:8000/dashboard/`.

Choose **Gyromite** and select **Run Demo Sequence**. The finite sequence demonstrates a single gate pressed with an unspun gyro, two spinning gyros on separate pads, one spin-down and re-spin recovery for each, and a final return to both holders. **Home** resets immediately. Stack-Up demonstrates red moving alone to Tray 4, followed by blue and white moving together to Tray 2. Its local command controls can move any valid block group; **Home** restores all five to Tray 3. Pose Lab is a character-only movement sandbox. All graphics are original SVG/CSS drawn for this project; the current preview uses no game or hardware connection.

## Connected system and camera experiments

1. RetroPie renders the game on an LCD or OLED screen. Its frame link sends each NES light cell to the UNO Q controller. The optional camera watches the command area for preview and Test checks.
2. A validated command changes the UNO Q's virtual R.O.B. pose and accessory model. The browser polls that state every 500 ms and shows the action.
3. In Gyromite, a virtual gyro or a held unspun gyro presses a virtual red or blue pad. The UNO Q sends the corresponding Controller 2 button state to the paired game host over LAN. When the virtual pad releases, the button releases.
4. In Stack-Up, commands move virtual blocks among five trays. The game modes documented in the manual have no Gyromite-style tray-button return path.

The RetroPie launch hook identifies an exact configured game filename, following the VirtualGlove approach. The [resolver](tools/identify_game.py) and [registry](config/games.json) match names; the installed test-machine hooks notify the UNO Q. A launch name supplies context; optical flashes remain the command source. User-supplied ROMs stay outside this repository.

## Guides

Start with the [documentation index](docs/INDEX.md), [user guide](docs/USER_GUIDE.md), [gameplay guide](docs/GAMEPLAY_GUIDE.md), and [virtual system contract](docs/VIRTUAL_SYSTEM.md). The [technical architecture](docs/TECHNICAL_ARCHITECTURE.md), [ROM signal analysis](docs/ROM_SIGNAL_ANALYSIS.md), and [verification plan](docs/VERIFICATION_PLAN.md) describe the implemented system and remaining camera validation.

Printable editions: [User Guide](output/pdf/R.O.B.-Vision-User-Guide.pdf), [Technical Reference](output/pdf/R.O.B.-Vision-Technical-Reference.pdf), [Matrix Display Guide](output/pdf/R.O.B.-Vision-Matrix-Display-Guide.pdf), and [Quick Reference](output/pdf/R.O.B.-Vision-Quick-Reference.pdf).

Historical Nintendo manuals and the Robert project inform behavior, but their text or code is not reused in this implementation. Game artwork and Nintendo marks remain with their owners.
