# R.O.B. Vision 0.3.0

Release preparation: this version has not been published. The latest published stable release remains 0.2.0.

## Changes

- Bundle Controller Router library 0.3.0 and independent UNO Q runtime 0.3.2, matching VirtualGlove 0.7.0. The runtime version prevents older 0.3.1 product bundles from replacing the prepared shared service.
- Include explicitly registered native RetroPie host adapters, merged input and Daphne exit handling in the shared build. Buddy's own game integration still requires its registered NES launch and frame-link paths.
- Expand Players and Systems to supported RetroArch and registered native adapters while preserving existing assignments, emulator commands and saved controls.
- Recover the UNO Q entry page without restarting Docker, either product service or the Matrix app. Healthy entry containers remain running.
- Report the active console's receiver status instead of implying that another console's check-in connects the selected game. Idle frame status is distinct from an active game link.
- Add Python and dashboard CI, compatibility fixes and refreshed shared guides. Full application jobs and scoped Python 3.7 console jobs have different support boundaries.

## Validation and remaining acceptance

The promoted development revision passed all 11 CI jobs across the three projects. The current RetroPie merged input paths and UNO Q entry-page recovery have scoped development evidence; automatic entry recovery completed in 15.7 seconds without restarting product or Matrix services. These checks do not certify the final release packages or every supported platform.

Build the final source archive, installer, manuals and checksums from a clean committed release revision. Qualify candidate installation, upgrade, rollback and both product installation orders on staging hardware. Briefly check Buddy input, exit, reconnect and app selection through the candidate's actual console/core. Preserve pairings, registered game names, player assignments, settings and controls. The independent Matrix firmware remains 0.2.0.

The release contains no ROMs. Separate uncommitted skin and UI development is excluded. Existing stable installation links continue to select 0.2.0 until a new release is published.
