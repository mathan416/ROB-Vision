# R.O.B. Vision 0.3.2

Stable release: 17 November 2026. The preceding stable release was 0.3.1.

## Changes

- Bundle Controller Router library 0.3.2 and independent UNO Q runtime 0.3.5, matching VirtualGlove's shared Router source.
- Reinstalling R.O.B. Vision or VirtualGlove on the UNO Q no longer leaves a lasting "No such file or directory" error on the Apps page. If an installer is replacing an app's folder while the Router writes its input lease, the next check a quarter of a second later rewrites it and the message clears.

## Validation

The source passed the R.O.B. Vision suite and the shared Router suite with bundled code synchronized. On the UNO Q that showed the original error, this R.O.B. Vision build installed the updated runtime: both apps and the Matrix were ready, the Apps page showed no error, and input leases were rewritten every check. Console software is unchanged from 0.3.1.
