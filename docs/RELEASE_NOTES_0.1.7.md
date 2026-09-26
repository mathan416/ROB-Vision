# R.O.B. Vision 0.1.7

This release makes console pairing and game identification easier to manage, broadens Batocera installation checks, and publishes Buddy's three-part **Big Wide Window** newspaper story.

## What changed

- **Per-console ROM registry:** Setup can open **Edit ROMs** beside each paired console. The editor validates exact NES filenames, saves them on that console, applies its emulator choices, and keeps edits through installer upgrades.
- **Console names and re-pairing:** UNO Q pairing resolves `.local` console names through its Avahi bridge. When a console is paired to another UNO Q, the receiver updates its target address; each console controls one UNO Q at a time. An UNO Q can remember several consoles.
- **Batocera preflight:** The installer selects FCEUmm or Nestopia wrappers for cores available on the device. The package includes wrappers for x86_64, 32-bit x86, AArch64, ARMv7, ARMv6, and RISC-V 64; if a packaged wrapper cannot load, a native C compiler can build one. Live Batocera device testing covered 43.1 x86_64. Other architectures are checked before installation changes the device but have not all been tested on physical hardware.
- **Browser polish:** Mission, Setup, and Help share the live connection label, clock, and Buddy icon. The website's About page now preserves the Mission image's proportions.
- **Buddy's story:** Episodes 1, 2, and 3 of *Buddy & the Big Wide Window* replace the earlier comic in the website, built-in Help, and release downloads. Earlier art remains in the source archive.

The same one-command installer handles first installation and upgrades on the UNO Q and on RetroPie or Batocera. Existing pairing data is retained during upgrades. No ROMs are included.

## Checks

Automated controller, receiver, registry, installer, and platform tests passed. The new receiver and installer source also compiled under RetroPie's Python 3.7.3. Both UNO Q dashboards and their paired console links were checked live. See [Technical Test Results](TEST_RESULTS_TECHNICAL.md) for the game-frame and optical test history.
