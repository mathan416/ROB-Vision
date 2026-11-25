# R.O.B. Vision 0.4.3

Stable release: 24 November 2026. The preceding stable release was 0.4.2.

## Changes

- Bundles Controller Router 0.4.1. On the UNO Q, R.O.B. Vision, VirtualGlove and the Controller Router page now run on the App Lab base image that App Lab itself uses (python-apps-base 0.13.2 today), and older copies of that image are removed when the services start. This frees about 900 MB on the UNO Q's small system disk.
- The Controller Router page warns when the UNO Q's system disk has less than 1 GB free, and its Help explains how to free space.
- The UNO Q installer now installs the boot-order and console-halt helpers itself, asking for the arduino password through `sudo`, as VirtualGlove's installer does. When it cannot ask, it prints the `NEXT` command as before.
- The UNO Q release command downloads and unpacks under the arduino home instead of `/tmp`, which is a RAM disk on the UNO Q, and removes its working folder afterwards.
- Controller Router refuses a second Router installation while one is running, so R.O.B. Vision and VirtualGlove upgrades on the same UNO Q can no longer interleave. It also stops copying retired files and old `.before-…` backup copies into the installed Router, and removes any it finds there.

Console software is unchanged from 0.4.2 apart from the bundled Controller Router library, now 0.4.1.

## Validation

The source passed the R.O.B. Vision suite on Python 3.9, 3.12 and 3.13, and the RetroPie receiver and Router tests on Python 3.7. Pre-releases 0.4.3-rc.1 to rc.4 were installed with the release commands on two UNO Q boards and a RetroPie console. Pairing was retained, the boards' tokens, keys and pairing files were unchanged, and each board kept a single `rob-vision.previous` backup. The new tests cover the sudo step (with and without a terminal), the download location, the install lock, and keeping retired files out of the installed Router.
