# Controller Router

## Choose a controller app on the UNO Q

Start a registered game on the paired console and Controller Router selects its app automatically. Gyromite and Stack-Up select R.O.B. Vision; games registered with VirtualGlove select VirtualGlove. You do not need to open either website to play. Both websites and Linux services stay running, but only the game's app controls input and the UNO Q Matrix. Router releases that control and shows its neutral animation when the game ends.

Open the UNO Q's `.local` address or LAN IP address without a port when you want to view or manually select an app. If only one app is installed, the page opens it directly; if both are installed, it shows a chooser. **Choose controller** in either app returns to the chooser. Opening a product's direct browser address selects it when no game is active. Finish a live game before changing apps manually.

Controller Router owns the UNO Q Matrix firmware. At startup, neither app is selected and the Matrix shows Router's neutral animation. A registered game selects its app and displays that app's cues. If Router stops or the UNO Q restarts, input stops until the running game's console session is reported again. Pairing and manual controller changes are blocked during a live game.

R.O.B. Vision's browser uses port **8101**. Its console receiver continues on port **8766**. This UNO Q app chooser is separate from the console player assignments described below.

Controller Router decides which game controller supplies each player in RetroArch. R.O.B. Vision installs it on RetroPie and Batocera so Buddy's virtual buttons and your physical gamepads can coexist. Your console still uses its original controllers in EmulationStation; Router takes over their game input only while a Libretro game is running.

## What goes to each player

| Source | Usual assignment | What it does |
| --- | --- | --- |
| Your physical gamepad | Player 1 | Moves Hector, selects a mode, starts the game, and provides the console's normal menu and exit controls. |
| Buddy (R.O.B. Vision Controller 2) | Player 2 | Presses Gyromite's red and blue gates when a gyro rests on a pad or you use Fast Gates. Buddy's visible Stack-Up movements come from decoded game frames. |
| Another physical gamepad | Any chosen player | Can share a player with another pad or control a different player if the game supports it. |

**Buddy stays on Player 2.** On a new Router installation, gamepads already configured in EmulationStation are suggested in Player 1–4 order. If Router was already installed with VirtualGlove, R.O.B. Vision keeps its saved assignments and adds Buddy to Player 2. A controller's Linux `jsN` number and RetroArch pad number can change after reboot; use the named assignments in Setup instead of editing those numbers.

Router assigns controller *sources* to player slots. It does not alter an NES game's player count, the ROM registry, the game-frame link, or the buttons you mapped in EmulationStation. A physical controller may share Buddy's Player 2 slot, but it will then send Player 2 input during Libretro play.

## Review or change assignments

1. Open the live UNO Q **Setup** page and find **Console Link**.
2. Choose **Controllers** beside the console you are playing. The Controller Router card selects that console and shows its saved assignments.
3. Check which physical gamepad is Player 1. If you use more than one console, review each separately; each console saves its own Router settings.
4. Choose **Test Inputs**, then press a direction or button on each connected gamepad during the five-second test. The result tells you which controls were seen. A pad can be connected yet show no activity if you did not press it during the test.
5. To change an assignment, exit the RetroArch game, choose the desired player beside that physical gamepad, then select **Save Assignments**. Relaunch the game to use the new routing.

**Reload** fetches the current console assignments and discards unsaved choices on the page. **Restore Previous** returns to the last saved assignment; it is available only when a previous save exists. Buddy's Player 2 choice cannot be changed in R.O.B. Vision Setup.

## What the status means

- **Connected:** Router can see that configured physical controller now.
- **Unavailable:** A saved controller is not present or its identity no longer matches. Reconnect the same pad. If you replaced it, configure the replacement in EmulationStation, then assign it in Router.
- **Mapping updated:** EmulationStation has a newer valid button map for the same controller. Router keeps its player assignment and uses the refreshed map at the next game launch.
- **No input detected:** No button or direction was pressed during the test. Try again while moving the pad; this result alone does not prove the pad is broken.

The merged Player 1–4 devices stay neutral in EmulationStation. Test the original gamepad there, then test its merged player inside a Libretro game.

## When a controller seems wrong

**My gamepad works in EmulationStation but not in the game.** Try another connected gamepad first. The one in your hands may be Player 2 while another is Player 1. Review the names and assignments in Setup, use **Test Inputs**, and correct the slot with the game closed.

**Hector moves but Gyromite's gates do not.** Player 1 working does not prove Buddy's Player 2 path. Check that Buddy appears on Player 2, the console link is online, and Gyromite is running through a R.O.B. Vision FCEUmm or Nestopia choice. On the game screen, test one gate at a time with **Lower Blue** or **Lower Red** in Setup, then choose **Release Both**.

**Buddy moves on Mission but a physical pad does nothing.** Confirm that the pad is assigned to the player you intend, then check its activity. If it was remapped in EmulationStation, close and relaunch the game. Do not change RetroArch's generated joypad index to chase a changing device number.

**A controller disappeared after it was unplugged.** Reconnect the saved pad and reload the card. Router releases held input from a disconnected source. If the old pad is gone permanently, assign its replacement and save while no game is running.

For installation and pairing, see [Installation and Setup](INSTALLATION_AND_SETUP.md). For game-specific checks, see the [Game Manual](GAME_MANUAL.md) and [Troubleshooting](TROUBLESHOOTING.md).
