# RetroPie connection

The dedicated `retropie.local` test machine runs the launch/end scripts in this folder and `rob-vision-controller2.service`. The scripts notify the UNO Q at `http://arduiain.local` using a private token file at `/home/pi/.config/rob-vision/token`. They allow game launch to continue if the UNO Q is unavailable. The service polls the UNO Q's current Gyromite pad state about every 50 ms, creates a Linux virtual joystick through `/dev/uinput`, and releases both buttons after 750 ms without a good read or when the Gyromite RetroArch process is absent. It scans active RetroArch processes and resends exact game identity after a UNO Q restart. No ROM or token is stored in this repository.

After installing the receiver, run `python3 /home/pi/rob-vision/tools/retropie_pair.py` on RetroPie and enter its one-time code and SHA-256 fingerprint in the UNO Q [Setup page](../../dashboard/setup.html). This copies the UNO Q controller token to the receiver over a certificate-pinned TLS connection. The receiver marks the Setup link online through authenticated polls. The pairing helper does not install the receiver, RetroArch configuration, or launch hooks.

The current NES-specific RetroArch configuration forces Player 2 to Gamepad (`input_libretro_device_p2 = "1"`) and assigns joystick index 1 to Controller 2. The receiver emits red as Linux button 0 and blue as button 1. In a real Game A test, button 0 initially moved the visible blue gate, so the RetroArch profile and NES config now map button 1 to A and button 0 to B. After a restart, an isolated blue hold moved the blue gate and release returned it. The player subsequently confirmed that both red and blue controls work in Game A. `--swap-buttons` on the receiver is an alternative way to reverse the two colors, but is not enabled on this machine. RetroArch reads the NES configuration when a game starts, so restart Gyromite after installing or changing its mapping.

The service is enabled through systemd and should be running before the game launches. Its status is available with `systemctl status rob-vision-controller2.service`; the virtual pad should appear as `/dev/input/js1` while the existing player's controller is `/dev/input/js0`. The UNO Q app must be running in App Lab. Its attached camera has recognized Test signals in both games; camera movement reception was intermittent.

## Game-frame link

The FCEUmm and Nestopia proxies observe the NES image one emulated frame at a time. Each sends a black/green/other classification and frame number to the receiver over `/run/rob-vision/frames.sock`. The receiver accepts only a RetroArch process using one of these exact proxies with a Gyromite or Stack-Up ROM found in the game registry. A complete 13-frame command travels to the UNO Q using the paired token. This path avoids the camera's one-frame sampling limit. The camera remains useful for preview, placement, and Test mode. Mission says **GAME FRAMES LINKED** when the current RetroPie game is sending frames.

The `lr-robvision-*` names are **RetroPie launch choices, not new emulators**. Each choice starts RetroArch with a small R.O.B. Vision wrapper around the installed, unmodified libretro core:

| Choose for Gyromite or Stack-Up | Emulator that actually runs the game | Automatic frame link |
| --- | --- | --- |
| `lr-robvision-fceumm` | FCEUmm | Yes |
| `lr-robvision-nestopia` | Nestopia | Yes |
| `lr-fceumm` or `lr-nestopia` | The named core directly | No |

The plain core choices still play the game. Without a R.O.B. Vision wrapper, the camera can watch the screen for optical commands, but camera-only movement is still experimental; manual controls and demos remain available. The wrapper reads the rendered light signal and forwards the original video to RetroArch. It does not replace or modify the emulator core. The two R.O.B. Vision entries are registered for the NES system, and the per-game overrides apply only to the registered Gyromite and Stack-Up ROMs.

Copy `rob_vision_fceumm_proxy.c` to `/home/pi/rob-vision/build/` and build each installed core:

```sh
gcc -std=gnu11 -O2 -fPIC -shared -Wall -Wextra -o /home/pi/rob-vision/build/rob_vision_fceumm_libretro.so /home/pi/rob-vision/build/rob_vision_fceumm_proxy.c -ldl
gcc -std=gnu11 -O2 -fPIC -shared -Wall -Wextra -DROB_USE_NESTOPIA -o /home/pi/rob-vision/build/rob_vision_nestopia_libretro.so /home/pi/rob-vision/build/rob_vision_fceumm_proxy.c -ldl
```

Copy `tools/retropie_frame_hook.py` and `tools/install_retropie_frame_hook.py` into `/home/pi/rob-vision/tools/`, then run `sudo python3 /home/pi/rob-vision/tools/install_retropie_frame_hook.py`. It registers `lr-robvision-fceumm` and `lr-robvision-nestopia`, backs up changed RetroPie configuration, and preserves each game's existing FCEUmm or Nestopia choice. It leaves other NES games and the NES default alone. To switch just Stack-Up, run `sudo python3 /home/pi/rob-vision/tools/install_retropie_frame_hook.py --stack-up-core nestopia`; `--gyromite-core` works the same way. Use `fceumm` to switch back. Restart the receiver service after updating its script, and restart the selected game to load its new proxy. The current test machine has both choices registered and delivered live commands from both games under Nestopia. Both games were restored to FCEUmm afterward; Nestopia's Gyromite Player 2 gate return has not yet been observed in Game A.

On this RetroPie, the existing Sony controller profile had Start assigned as both game Start and emulator Exit. It prevented Gyromite from starting. A later profile reused Select as RetroArch's hotkey modifier, which conflicted with Stack-Up's mode navigation. The current profile reserves Start (button 8) and Select (button 9) for the games. L3 (button 11) is the hotkey modifier and R3 (button 12) is Exit; L3+R3 was confirmed to exit Stack-Up cleanly. Sony Start entered Stack-Up Test, and its Select was tested against the Test display. The connected keyboard's Escape key is also configured to exit RetroArch. The original profile is backed up beside it as `Sony Computer Entertainment Wireless Controller.cfg.before-rob-vision`; the intermediate profile is backed up as `.cfg.before-stackup-select`. Restart the game after any mapping change.

FCEUmm remains the default NES core. Its [controller documentation](https://docs.libretro.com/library/fceumm/) describes the regular Player 1 joypad and selectable Player 2 device. The NES configuration forces Player 2 to Gamepad for Gyromite's virtual buttons; Stack-Up uses Player 1 to select Test, Direct, Memory, or Bingo. On the ROBOT BLOCK artwork, use game Select to show the mode list, then game Start to enter the selected mode. Test flashes alternate green and white over that artwork, so it can look like the title screen while the Test signal is active.

On another RetroPie machine, inspect existing runcommand scripts and merge the calls rather than replacing other projects' hooks. The test machine had no custom scripts before installation. Back up the NES RetroArch configuration before adding the four Controller 2 lines above its `#include` line. Protect the UNO Q token file with owner-only permissions. The copies on the test machine are in `/home/pi/rob-vision/`; the NES config backup is `/opt/retropie/configs/nes/retroarch.cfg.before-rob-vision`.
