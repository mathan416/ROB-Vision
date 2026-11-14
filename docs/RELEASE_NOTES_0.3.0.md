# R.O.B. Vision 0.3.0

Stable release: 14 November 2026. The preceding stable release was 0.2.0.

## Changes

- Bundle Controller Router library 0.3.0 and independent UNO Q runtime 0.3.3, matching VirtualGlove's shared Router source. The runtime version prevents older 0.3.2 product bundles from replacing the shared service.
- Include explicitly registered native RetroPie host adapters, merged input and Daphne exit handling in the shared build. Buddy's own game integration still requires its registered NES launch and frame-link paths.
- Expand Players and Systems to supported RetroArch and registered native adapters while preserving existing assignments, emulator commands and saved controls.
- Preserve saved game registrations and Router source choices byte for byte during UNO Q and console upgrades.
- Recover the UNO Q entry page without restarting Docker, either product service or the Matrix app. Healthy entry containers remain running.
- Report the active console's receiver status instead of implying that another console's check-in connects the selected game. Idle frame status is distinct from an active game link.
- Add optional Buddy skins with bounded PNG and SVG artwork packs, preview, import/export, and a starter pack and artist guide. Gyromite gyros and Stack-Up blocks retain their original game art.
- Add Python and dashboard CI, compatibility fixes and refreshed shared guides. Full application jobs and scoped Python 3.7 console jobs have different support boundaries.

## Validation and remaining acceptance

The final source passed 121 Python tests, 10 dashboard tests, package checks, and CI on both `dev` and `main`. The installer archive, guides, and attached assets were checksum-verified. The release-candidate runtime was installed on the paired and separate test UNO Qs and the RetroPie cabinet. Both UNO Qs passed post-upgrade reboot checks with Router, Matrix and both products healthy, and 15 selected protected files preserved on each; the cabinet retained 13 selected protected files and its emulator configuration. The owner reported that the requested cabinet control and exit checks, including a R.O.B. Vision game, passed.

The independent Matrix firmware remains 0.2.0. New pairing, reconnect, a fresh installation in both product orders, full UNO Q rollback, live skin import, and hardware acceptance on console platforms beyond the tested cabinet were not established by these checks. Installers retain recovery backups and protect saved game registrations and Router source settings.

The release contains no ROMs. Skin import/export has automated and guide checks; use the Setup preview to confirm an artwork pack on the target display.
