# Release review — 25 September 2026

**Decision:** suitable for continued RetroPie and UNO Q testing; hold a general release until the live checks below are complete. This review covers the controller, dashboard, RetroPie receiver and frame wrappers, tests, and current guides. It is a code and local test review, not a new hardware endurance test.

## Cleanup

- Removed the UNO Q camera capture service, optical sample decoder, Kiyo Pro configuration, recovery helper, camera endpoints, camera setup controls, and camera-specific dependency and tests.
- Retained the ROM-derived 13-frame decoder in the RetroPie receiver. FCEUmm and Nestopia wrappers continue to feed it complete rendered NES frames.
- Moved game Test-signal detection to the RetroPie frame stream. The receiver reports it through authenticated state polling so Setup and the matrix can show Test activity without camera input. This new path has local automated coverage but has not yet been verified in a live Test-mode session.
- Updated current player, installer, technical, and built-in Help content to describe frame-link-only play. The dated camera reports remain archived research.
- Synced the updated app to `arduiain.local` and restarted its App Lab container. Synced the frame decoder and receiver to `retropie.local` and restarted the receiver service while no game was running.

## Checks run

| Check | Result |
| --- | --- |
| Python unit suite | 34 passed, including both game models, frame command decoding, frame Test detection, receiver, game identification, and matrix state. |
| JavaScript Stack-Up model suite | 5 passed. |
| Python compilation and dashboard JavaScript syntax | Passed. |
| Source scan | No camera capture, camera recovery, OpenCV dependency, or camera controls remain in runtime code. |
| Live UNO Q HTTP smoke | `/api/state` has no camera state; Setup serves successfully; the old camera endpoint returns 404. RetroPie receiver service is active. |

## Checks still needed for a general release

1. Verify Gyromite and Stack-Up Test-mode light acknowledgement through the live frame link after both the UNO Q app and RetroPie receiver have the updated code.
2. Confirm Gyromite red and blue Controller 2 gate return in Game A with the Nestopia launch choice. The FCEUmm mapping was player-confirmed; Nestopia frame commands were checked, but its gate return was not checked in Game A.
3. Run longer interactive sessions and repeated launch/exit cycles for both games, including Stack-Up Memory and Bingo. Current live evidence covers all six commands in Direct play, not endurance or every mode.
4. Check the panel from laptop, phone, and iPad together and verify reconnection after a UNO Q restart.

See the [verification plan](VERIFICATION_PLAN.md), [FCEUmm frame-link report](FRAME_LINK_TEST_2026-09-25.md), and [Nestopia report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md). Historical camera results are in the [archived live optical report](LIVE_OPTICAL_TEST_2026-09-25.md).

## 0.1.0 Nestopia follow-up

Batocera Game A blue-gate hold and release passed after the wrapper selected Nestopia explicit Player 2 gamepad device `257`. RetroPie Nestopia still needs the same live return-path check. Stack-Up movement under Nestopia was observed in earlier Direct-mode sessions.
