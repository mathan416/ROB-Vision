# R.O.B. Vision 0.4.2

Stable release: 19 November 2026. The preceding stable release was 0.4.1.

## Changes

- Upgrading R.O.B. Vision on the UNO Q now keeps a single backup of the version it replaced, as `rob-vision.previous`. Previously each upgrade added another numbered `rob-vision.previous-…` copy and nothing removed the old ones; one UNO Q had built up 31 copies, several gigabytes in all. The first 0.4.2 upgrade also removes any older numbered copies.
- A failed upgrade still restores the previous version, and failed candidates (`rob-vision.failed-…`) are still kept for inspection. If a backup cannot be removed, the installer prints a note and the installation still completes.
- Updated 2026-11-24: installing on the UNO Q no longer stops when flashing the Controller Router Matrix sketch to the board fails once ("Upload port detection failed"). The installer now tries the flash up to three times. Upgrades keep App Lab's sketch build folder, so a changed Matrix sketch recompiles only what changed, and a rerun after a failed first install reuses that attempt's build.

## Validation

The source passed the R.O.B. Vision suite. The UNO Q upgrade test now runs a third upgrade with older numbered copies and a failed candidate present, and checks that only the current app, the replaced version and the failed candidate remain; it fails without this change. Console software and the UNO Q runtime are unchanged from 0.4.1. The 2026-11-24 update changes only the Controller Router installer; its tests cover a retried flash, a compile error that is not retried, and the kept build cache.
