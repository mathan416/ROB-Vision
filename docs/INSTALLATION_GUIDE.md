# R.O.B. Vision installation guide

**Installed test setup, 25 September 2026:** R.O.B. Vision is a separate UNO Q App Lab app. `retropie.local` has exact-name launch/exit hooks, pairing, a virtual Controller 2 receiver, and FCEUmm and Nestopia frame-link choices. Gyromite launch/exit and both gate colors were verified under FCEUmm. Both games delivered commands through FCEUmm and Nestopia. Nestopia's Gyromite Player 2 gate return still needs a Game A check. There is no physical robot or camera.

## UNO Q and browser

Start **R.O.B. Vision** under App Lab **My Apps**. Stop VirtualGlove first because this UNO Q runs one App Lab app at a time. App Lab exposes port 80 at `http://arduiain.local/dashboard/`; the controller is also reachable at `http://arduiain.local:8766/dashboard/`. Both URLs share one virtual game state. The App Lab `python/main.py` gateway talks to `controller/service.py`, and Router Bridge drives the matrix sketch. Existing Avahi supplies the `.local` hostname. Keep the separate `deploy/rob-vision.service` disabled while App Lab owns port 8766.

Open [Setup](../dashboard/setup.html) to check pairing and the game-frame link. Browser controls are available on the trusted LAN without a token prompt. The token in the UNO Q's `~/.config/rob-vision/environment` authenticates RetroPie launches and receiver traffic. Keep the LAN private. A local `file://` page is an offline preview.

## RetroPie

Follow the [RetroPie deployment instructions](../deploy/retropie/README.md) for the launch/end hooks, root uinput receiver service, pairing, FCEUmm and Nestopia launch choices, and RetroArch port 2 configuration. Merge hooks with any existing scripts rather than replacing unrelated commands. After pairing, **Check Link** turns online when authenticated receiver polls arrive. The receiver can resync game identity from the active RetroArch process after a UNO Q restart.

For Gyromite or Stack-Up, choose `lr-robvision-fceumm` or `lr-robvision-nestopia` in RetroPie's emulator selection. These entries run the installed original core through R.O.B. Vision's frame wrapper. Plain `lr-fceumm` and `lr-nestopia` play without automatic R.O.B. movement. The UNO Q receives only complete game-specific light commands. Setup's Test check uses the same frame link.

## Local development

Run `python3 -m controller.service` and open `http://127.0.0.1:8766/dashboard/`. For trusted-LAN access set `ROB_VISION_TOKEN` and use `--host 0.0.0.0`; the token protects RetroPie traffic, while browser controls are available on that LAN. The static preview can be served with `python3 -m http.server 8000` and has no game link.

Run the [verification plan](VERIFICATION_PLAN.md) before a general release.
