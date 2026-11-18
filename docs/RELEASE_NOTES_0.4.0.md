# R.O.B. Vision 0.4.0

Release candidate 1: 18 November 2026. The preceding stable release was 0.3.2.

## Changes

- Bundle Controller Router library 0.4.0 and independent UNO Q runtime 0.4.0, matching VirtualGlove's shared Router source.
- A paired RetroPie console can halt the controller when you choose **Shutdown System** in EmulationStation. Turn on **Halt this controller when the console shuts down** for that console in secure Setup; the change asks for the Matrix code. Quit and Restart choices never halt it, and the controller stays running while a game is active on it or another paired console is connected.
- The UNO Q installer's printed administrator command now installs the controller halt helper together with the boot-order helper. Run it once with `sudo` to use the halt setting.
- The console installer adds the EmulationStation shutdown hook and a bounded, root-only notifier. If the controller cannot be reached, the console shuts down normally.
- Every UNO Q portal page links to **Console setup**.

## Validation and remaining acceptance

The source passed the R.O.B. Vision suite and the shared Router suite with bundled code synchronized. A development build of this source was installed on the paired UNO Q and a RetroPie console, the halt helper was installed with the administrator command, and choosing **Shutdown System** halted the UNO Q cleanly. With the setting off, the request was refused and the UNO Q kept running. Batocera and Recalbox consoles do not send the request yet.
