# Release review — 25 September 2026

**Decision:** suitable for continued RetroPie and UNO Q testing; hold a general release until the live checks below are complete. This review covers the tracked controller, dashboard, RetroPie receiver and frame wrapper, UNO Q host helpers, tests, and shipped guides. It is a code and local smoke review, not a new hardware endurance test.

These cleanup changes were verified locally. The running UNO Q app was not restarted or replaced during this review.

## Cleanup and corrections

- Removed the camera's unused wide-frame and 12-band measurements from the 60 fps capture loop and diagnostic response. The active crop, timestamped trace, preview, Test detector, and optical decoder remain. The band results in earlier research reports remain historical evidence.
- Removed an unused command argument and corrected an outdated dashboard comment.
- Served PDF, image, and font assets with their proper media types and made static assets refresh on reload. A local HTTP smoke check fetched the dashboard, JavaScript, PDF, and font with the expected headers.
- Rejected non-finite saved or browser-supplied camera regions before capture starts.
- Updated the optical input reference and its printable Technical Reference edition.

## Checks run

| Check | Result |
| --- | --- |
| Python unit suite | 50 passed. Covers both game models, optical patterns, receiver, game identification, matrix state, and UNO Q helpers. |
| JavaScript Stack-Up model suite | 5 passed. |
| Python compilation and dashboard JavaScript syntax | Passed. |
| Static dashboard links | No missing local assets found. |
| Local controller HTTP smoke | State, dashboard, JavaScript, PDF, and font responses succeeded. |
| Technical Reference layout | Updated optical-input page rendered and inspected. |
| Tracked secrets and ROM archives | No token files, credentials, ROM ZIP/7z files, or generated Python caches are tracked. |

## Checks still needed for a general release

1. Confirm Gyromite's red and blue Controller 2 gate return in Game A while using the Nestopia launch choice. The FCEUmm mapping was checked with the player; Nestopia's frame commands were checked, but its gate return has not been checked in Game A.
2. Run longer interactive sessions and repeated launch/exit cycles for both games, including Stack-Up Memory and Bingo. Current live frame-link evidence covers all six commands in Direct play, not endurance or every mode.
3. Check the live panel from a laptop, phone, and iPad at the same time and verify reconnection after a UNO Q restart. The automated suite checks the underlying state, but this device combination has not been exercised.
4. Treat camera-only movement as experimental. The camera recognizes both Test signals and some Stack-Up movements, but one-frame flashes were missed during live 60 fps capture. The RetroPie frame link is the reliable input path measured so far.
5. Install and validate the optional UNO Q host recovery helpers only if that startup and USB recovery behavior is part of the release. App Lab does not install those units automatically.

See the [verification plan](VERIFICATION_PLAN.md), [FCEUmm frame-link report](FRAME_LINK_TEST_2026-09-25.md), [Nestopia report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md), and [camera report](LIVE_OPTICAL_TEST_2026-09-25.md) for the underlying observations.
