# R.O.B. Vision 0.2.0 candidate review

Reviewed 29 September 2026 against `dev` for the next minor release. This review does not publish a candidate. The stable installation commands remain on the published `0.1.7` release until candidate assets are built and accepted.

## Result

- All 113 Python tests pass after adding the next-minor package-tag regression. The shared Router library and UNO Q portal match their source project and the VirtualGlove bundle.
- The release packager now accepts semantic release tags including `v0.2.0-rc.1` and `v0.2.0`; it still rejects malformed tags. This removes the previous `0.1.x` packaging limit.
- Retired persistent RetroArch writers and the old UNO Q early-start service are removed. Game launch and receiver startup do not rewrite a saved `retroarch.cfg`.
- A tracked-filename check found no ROM, private-key, or credential files. It is a limited packaging check, not a complete security audit.

## Candidate acceptance still required

1. Build and install the candidate from the reviewed commit; verify the release installer and checksums from downloaded assets.
2. Test Gyromite gates and Stack-Up movement through both FCEUmm and Nestopia on RetroPie and Batocera, including launch, exit, Test mode, and the first command after automatic selection.
3. Verify pairing, registered game names, reboot recovery, controller sleep/wake, and unchanged saved RetroArch configuration. Test both product installation orders on the UNO Q.
4. Confirm the UNO Q Help and downloadable PDFs correspond to the candidate before final `0.2.0` publication.

Earlier live gate and block tests remain dated evidence for their builds; they do not automatically certify this candidate.

## Recalbox development validation — 29 September 2026

Recalbox 10.1.1 on the `rpizero2` target paired with arduiain.local. Gyromite
and Stack-Up launched through the installed frame wrappers, selected R.O.B.
Vision, and cleared their sessions on exit. The player then confirmed a
Stack-Up Direct-mode command moved Buddy on Mission. Super Glove Ball selected
VirtualGlove and responded to input. Controller Router's Recalbox launch adapter
now maps the merged controller's Hotkey + Start to exit; the player confirmed
PlayStation Home + Start exited a fresh Super Glove Ball session. A visible
Gyromite blue/red gate test remains for candidate acceptance. These checks used
development installations, not downloaded candidate packages.
