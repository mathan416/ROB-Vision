# R.O.B. Vision 0.4.1

Stable release: 19 November 2026. The preceding stable release was 0.4.0.

## Changes

- The installer now checks which device it is running on before it downloads the release. Running the console command on an UNO Q previously downloaded the whole release and then reported an unsupported console. It now stops straight away and shows the UNO Q command to use instead: `sh -s -- uno-q`.
- Pairing does not affect either install. The UNO Q command installs whether the UNO Q is paired with no console, one console or several.

## Validation

The source passed the R.O.B. Vision suite, including a new test that runs the console command on an UNO Q and on an unsupported machine and confirms neither downloads the release. Console and UNO Q software is unchanged from 0.4.0.
