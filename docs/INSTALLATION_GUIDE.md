# R.O.B. Vision installation guide

**Available now:** the local browser preview, exact-name resolver, and Python controller service with optional OpenCV camera capture. **Planned:** validated UNO Q deployment and paired Gyromite game receiver. No physical R.O.B. assembly or motor calibration is needed.

For a local controller trial, run `python3 -m controller.service` from the project folder and open `http://127.0.0.1:8766/dashboard/`. Select a game and try a command; reload to confirm the controller retains state. Install `requirements-camera.txt` to enable **Start Camera**. The secondary camera tile shows a low-rate framing image with the sample region outlined; use `--camera-index` and `--camera-roi x,y,width,height` to start capture with a chosen crop. The reported fps is the delivered rate, not the requested rate. If serving over LAN, set `ROB_VISION_TOKEN` and pass `--host 0.0.0.0`; the dashboard asks for the token. The optional `tools/notify_game.py` helper can send exact RetroPie launch names but is not installed into the cabinet hooks automatically. The existing standalone preview at `dashboard/index.html` stays available without the service.

## Open the preview

From the project directory, serve the files locally with `python3 -m http.server 8000` and open `http://localhost:8000/dashboard/` on the same computer. Select a mode and run its finite demo. **Home** resets the preview; the browser **Emergency Stop** cancels only local scripted actions. The existing preview does not connect to the cabinet or UNO Q.

## Planned connected setup

1. Install the supported UNO Q system, camera, and project service after their exact versions and interfaces have been validated.
2. Mount the camera so the cabinet's game flash region stays in frame. Calibrate focus, exposure, and timing using the game's Test mode and capture trace.
3. Connect the UNO Q and game host over trusted Wi-Fi or Ethernet. Pair the Gyromite virtual Controller 2 sender and receiver, then test both button colors and their release on link loss.
4. Serve the dashboard from the UNO Q. Verify laptop, iPad, and phone clients receive a complete snapshot followed by ordered events.
5. Configure exact Gyromite and Stack-Up launch filenames if using the optional RetroPie hook. Verify unknown titles and game exit return to idle.
6. Test a complete optical-command-to-virtual-action loop, then a Gyromite virtual-pad-to-game response loop. Keep ROMs outside the project repository.

Do not invent install commands, UNO Q pin assignments, software versions, or supported camera modes before they are tested. A successful dashboard animation by itself is not proof of game compatibility. See the [verification plan](VERIFICATION_PLAN.md).
