# R.O.B. Vision installation guide

**Available now:** the browser preview, exact-name resolver, UNO Q controller service, optional OpenCV camera capture, and a paired Gyromite virtual Controller 2 receiver on `retropie.local`. No physical R.O.B. assembly or motor calibration is needed. A Game A gate response has been observed; camera behavior still needs live-game validation.

For a local controller trial, run `python3 -m controller.service` from the project folder and open `http://127.0.0.1:8766/dashboard/`. Select a game and try a command; reload to confirm the controller retains state. Install `requirements-camera.txt` to enable **Start Camera**. The secondary camera tile shows a low-rate framing image with the sample region outlined; use `--camera-index` and `--camera-roi x,y,width,height` to start capture with a chosen crop. The reported fps is the delivered rate, not the requested rate. If serving over LAN, set `ROB_VISION_TOKEN` and pass `--host 0.0.0.0`; the dashboard asks for the token. The `retropie.local` machine has the `tools/notify_game.py` helper installed in its runcommand hooks. The existing standalone preview at `dashboard/index.html` stays available without the service.

On the UNO Q, `app.yaml` and `python/main.py` make R.O.B. Vision a separate Arduino App Lab app under **My Apps**. App Lab publishes standard HTTP port 80 and controller port 8766. Open `http://arduiain.local` to reach the panel at the device name; the original `:8766/dashboard/` address remains available. Both addresses use the same controller state. This UNO Q's App Lab allows one app to run at a time: stop VirtualGlove before starting R.O.B. Vision. The controller token is copied privately to `data/controller-token` for App Lab; the same value is kept in `/home/arduino/.config/rob-vision/environment`. The optional user service template in `deploy/rob-vision.service` is disabled when App Lab owns the controller, because both cannot bind port 8766. App Lab's Python image already includes OpenCV. Camera capture cannot start until a real capture camera appears; `/dev/video0` and `/dev/video1` may be codec devices on UNO Q and are deliberately excluded. Camera capture and delivered fps still need hardware validation.

## Open the preview

From the project directory, serve the files locally with `python3 -m http.server 8000` and open `http://localhost:8000/dashboard/` on the same computer. Select a mode and run its finite demo. **Home** resets the preview; the browser **Emergency Stop** cancels only local scripted actions. The existing preview does not connect to the cabinet or UNO Q.

## Connected setup and remaining checks

1. Start the installed R.O.B. Vision app in UNO Q App Lab. Attach a compatible camera once its exact interface is validated.
2. Mount the camera so the cabinet's game flash region stays in frame. Calibrate focus, exposure, and timing using the game's Test mode and capture trace.
3. Connect the UNO Q and game host over trusted Wi-Fi or Ethernet. The `retropie.local` test machine has the [launch hooks and virtual receiver](../deploy/retropie/README.md) installed. Confirm both button colors in the game and release on link loss.
4. Serve the dashboard from the UNO Q. Verify laptop, iPad, and phone clients receive a complete snapshot followed by ordered events.
5. Verify exact Gyromite and Stack-Up launch filenames, unknown titles, and game exit returning to idle. A real Gyromite `.7z` launch and exit have selected and cleared the UNO Q game; a real Stack-Up launch remains to be checked.
6. Test a complete optical-command-to-virtual-action loop, then a Gyromite virtual-pad-to-game response loop. Keep ROMs outside the project repository.

Do not invent install commands, UNO Q pin assignments, software versions, or supported camera modes before they are tested. A successful dashboard animation by itself is not proof of game compatibility. See the [verification plan](VERIFICATION_PLAN.md).
