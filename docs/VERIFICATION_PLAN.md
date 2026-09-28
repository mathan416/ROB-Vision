# R.O.B. Vision verification plan

**Current evidence:** the preview, UNO Q app, real game launch and exit identification, live red/blue Gyromite gate response, and independent model flows have been verified. The console frame link decoded all six commands in both games during live Direct play and drove the UNO Q model. See the [game-frame report](FRAME_LINK_TEST_2026-09-25.md), [release validation](RELEASE_VALIDATION_0.1.0.md), and [unattended tests](UNATTENDED_TEST_REPORT_2026-09-24.md).

| Gate | Test | Pass condition | Status |
| --- | --- | --- | --- |
| Gyromite preview | Run the unspun one-gate press, dual relay, spin-down recovery, and cleanup | Pad states stay independent; after one recovery per gyro, both gyros return upright to holders, buttons release, and COMPLETE remains stable | Browser preview observed. |
| Preview reset | Use Home and demo restart at different phases | Timers, queue, pieces, and buttons return to initial state | Browser implementation; regression tests pass. |
| Stack-Up preview | Move red alone, then blue and white together; try a blocked release | Five blocks conserved, colors stay ordered, and invalid moves leave state unchanged | Browser observed; five model tests pass. |
| Frame Test signal | Enter Test mode in both games while the frame link is active | Red Test light blinks while no movement occurs | Automatic Test indication is implemented and verified in the linked game flow; repeat on each supported core during a full session. |
| Console game-frame link | Launch each registered ROM through EmulationStation and issue six Direct commands | Exact 13-frame command recognized, authenticated receiver forwards it once, UNO Q model applies or correctly blocks it | All six command types observed in both games; model state changed for valid commands and blocked invalid boundaries. Longer session and Memory/Bingo coverage remain. See the [frame-link report](FRAME_LINK_TEST_2026-09-25.md). |
| Game identity | Launch exact configured Gyromite/Stack-Up names and unknown titles | Correct context on start; idle on exit/unknown | Real Gyromite `.7z` launch and exit selected then cleared UNO Q context. The receiver now recovers Gyromite context after a UNO Q restart during a live game. Both games' installed hooks passed controlled start/end tests; Stack-Up booted headlessly in RetroArch. A real interactive Stack-Up `.7z` launch selected Stack-Up and its exit cleared the UNO Q. An unknown-title launch remains pending. |
| Gyromite LAN output | Send red/blue virtual states and disconnect | Correct Controller 2 mapping; button releases on virtual lift, timeout, exit, and reset | Both colors pressed/released at Linux input with Player 2 forced to Gamepad. Initial isolated red moved the blue gate. After swapping A/B and restarting, isolated blue moved the blue gate and released it. The player later confirmed both red and blue controls work in Game A. Automated stale-release checks pass; sustained physical link-loss observation remains pending. |
| Multi-client UI | Open laptop, iPad, and phone simultaneously | Same UNO Q snapshot and ordered events; reconnection does not reset game | Not run. |
| Shared UNO Q Matrix | Observe reboot, automatic selection, Test, pairing, and product restart | Neutral after boot/exit; only the selected product’s manifest cues appear; input follows the lease | Shared Router requests and lease guards have automated coverage. Complete visual checks of every animation remain open. The separate legacy product sketch is not the current installation path. |

## Shared Router follow-up — 27 September 2026

The dated optical and frame-link reports above remain evidence for those test configurations. Current installations use the shared Router Matrix firmware and one selected product lease; their behavior is described in the [Technical Reference](TECHNICAL_ARCHITECTURE.md) and [Controller Router guide](CONTROLLER_ROUTER.md).

| Check | Recorded result | Remaining boundary |
| --- | --- | --- |
| Live registered games on retropieconsole.local | The player confirmed Gyromite and Stack-Up work with R.O.B. Vision, and confirmed automatic VirtualGlove selection with Super Glove Ball and Gyruss. | These reports do not establish every core, mode, or platform combination. |
| Product web suites | R.O.B. Vision: 109 Python tests, one skipped; VirtualGlove: 107 web/control tests passed. | Automated and mocked checks are distinct from physical gameplay. |
| Shared chooser | Eight portal tests passed; mocked one-/two-app navigation checks passed. Both services were ready on arduiain.local after the navigation deployment. | The chooser opens already-running sites; this is not a new cold-install or reboot test. |
| Input lease and first-command protection | Code rejects missing/invalid boot-bound leases on managed installs; retains frame commands for up to 12 seconds; expires a lost R.O.B. session after ten seconds. | Repeat recovery and first-input checks in the next release candidate. |
| Wireless-controller hotplug | Sleeping or waking during a game can shift RetroArch’s device slots. The workaround is documented in both products’ Help. | Open routing defect; do not mark it resolved. |

For the next candidate, retain the clean-install and repeat-upgrade checks in both product orders, pairing/settings preservation, reboot recovery, simultaneous-session rejection, and visual Matrix checks. Complete VirtualGlove pairing from arduiain.local to retropie.local separately. No additional live test is claimed by this documentation update.
