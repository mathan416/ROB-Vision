# R.O.B. Vision 0.3.1

Release candidate 3: 17 November 2026. The preceding stable release was 0.3.0.

## Changes

- Bundle Controller Router library 0.3.1 and independent UNO Q runtime 0.3.4, matching VirtualGlove's shared Router source. The runtime version prevents product bundles carrying 0.3.3 or earlier from replacing the updated pairing pages.
- Close a console migration loophole: another device on the network could no longer take over a console that still had an unmigrated legacy pairing by asking it to sign its own migration proof.
- Secure Setup now asks for the code shown on the UNO Q Matrix before it removes a console or turns an app's access off or on. Only the page that started a confirmation can cancel it, and pairing with a valid console code takes priority over an unconfirmed change.
- Saving or rolling back console assignments keeps Buddy on Player 2.
- Restore the previous console connection once after a failed change, without blocking pairing for two minutes.
- Keep Setup and Players and Systems responsive while the UNO Q checks an unavailable console, and give a full ten-second controller test time to finish.
- The console Router no longer keeps a CPU core busy checking for a running game. It checks once a second and rescans processes only when one starts or exits; on the tested RetroPie console this fell from about 73% to 6% of one core. (RC2)
- The console Router's idle work no longer re-reads every input device each second; it checks only when controllers or their settings change. Measured idle load on the tested console fell from about 19% to 5% of one core (RC3).
- RetroPie, Batocera and Recalbox installers register the console adapter's variable name and UNO Q port explicitly. Existing registrations keep working.

## Validation and remaining acceptance

The source passed the R.O.B. Vision suite and the shared Router suite with bundled code synchronized. Before these version changes, the same source was installed on the paired UNO Q and the RetroPie cabinet. Every installer check passed, the console link service and receiver restarted, and the UNO Q reported the console connected with both apps ready after the cabinet rebooted.

Matrix-confirmed pairing changes on the hardware and gameplay with Buddy had not yet been checked when this candidate was prepared; they are required before the stable release. The Matrix firmware remains 0.2.0.
