# R.O.B. Vision technical test results

**Evidence window:** 24-26 September 2026. This report consolidates the dated engineering records for the supplied Gyromite and Stack-Up World ROM archives, a Razer Kiyo Pro watching a modern LCD, RetroPie, the Arduino UNO Q, and the supported Batocera 43.1 x86_64 host. It records what each test established, what it did not establish, and why the release uses libretro frame input. The camera experiments are historical; the current release has no camera input path. No ROM or extracted game image is distributed with R.O.B. Vision.

## Read the result at the right layer

The measurements answer different questions. A complete 13-frame word in a RetroArch recording proves that the **game emitted** a light message. A matching camera trace proves that this particular display/camera capture preserved it. A receiver `decoded` event proves that a complete game-appropriate word reached the receiver. A UNO Q `action` event proves that the virtual model accepted the move; a `blocked` event may instead be the correct result at a boundary. A visible Gyromite gate response proves that the virtual Controller 2 state also returned to the game. Test-mode light recognition proves only status detection, not movement.

| Stage | Signal inspected | Evidence of success | Important non-claim |
| --- | --- | --- | --- |
| ROM analysis | Program tables and palette selection | Expected dark/green command words | Does not measure live capture timing |
| Optical simulation | Synthetic sampled brightness traces | Decoder acceptance and rejection under modeled phase/jitter | Does not certify a physical camera |
| Live camera | Kiyo Pro frames from the LCD | Actual Test recognition or complete movement word | One decoded command is not a play-rate measurement |
| Source-aligned camera study | RetroArch recording plus camera trace | Which one-frame cells survived the display/camera path | A closest match is not a safe action |
| Libretro frame link | Every rendered NES frame before display | Exact decoded word and UNO Q model result | Does not reveal score or Hector's position |
| Player 2 return | Game A screen during isolated pad holds | Visible gate lower and return | Does not establish complete game automation |

## Reference signal and examined material

The examined games transmit **one primitive per message**. A data word is 13 rendered NES frames, `000101w1x1y1z`: `0` is dark and `1` is green. The four variable bits select Left, Right, Open, Close, or the game's own Up/Down code. Stack-Up adds a dark frame after the data word. Gyromite Test is a sustained green field; Stack-Up Test alternates light and dark on the ROBOT BLOCK artwork. A separate ready-light word is status only. Neither Test nor ready light is a movement.

The inspected Gyromite ZIP SHA-256 is `bf1b323ba39c84b964f93127598b267ff3f16cbf99c533ae1e9b8332232b3e5b`; Stack-Up is `3ab6bc99246783a6bf7083481027fe358ccdb147dcf1165eaf08aaf4e1b06548`. The ZIP and 7z copies of each game contained identical NES data. Both are iNES mapper-0 images with 32 KiB program ROM and 8 KiB character ROM. The [ROM signal analysis](ROM_SIGNAL_ANALYSIS.md) gives CPU addresses, palette evidence, every word, and the reproducing command. These hashes identify the examined copies, not every regional or patched ROM.

## Synthetic camera timing: useful warning, not acceptance

The first unattended run used deterministic synthetic light traces with random sampling phase, about 0.7 ms timestamp jitter, and small brightness noise. It exercised the decoder and virtual model, including gyro transfers, grouped Stack-Up blocks, wrong-game rejection, and idle/Test false triggers. Thirty seconds each of synthetic dark idle and alternating Test yielded **zero movement commands**. The then-current suite passed 29 Python and five JavaScript tests; a later documentation regression run passed 37 Python and five JavaScript tests. These counts describe the suite at those dates, not independent optical trials.

| Requested capture rate | Gyromite decoded | Stack-Up decoded | Combined | Interpretation |
| --- | ---: | ---: | ---: | --- |
| 60 fps | 661/700 | 186/200 | 847/900 | Some valid words missed |
| 90 fps | 687/700 | 200/200 | 887/900 | Diagnostic comparison, above target camera rate |
| 120 fps | 617/700 | 175/200 | 792/900 | Non-monotonic run-length ambiguity |
| 240 fps | 700/700 | 200/200 | 900/900 | Diagnostic ceiling, not an available camera mode |

A separate 900-transmission 30/60 fps study used a different seed and decoder revision. At **30 fps, 0/900** words were accepted. At **60 fps**, the original revision accepted **839/900** but sometimes selected the wrong action. A sampled-frame ambiguity guard accepted **667/900 correctly**, rejected **233/900**, and made **zero wrong selections in that run**. Ten further seeded 900-word runs also produced no wrong selection. That is a safety result for the tested synthetic distributions, not a bound on live misclassification probability. Some one-frame cells fell entirely between captures. The controller therefore requested 60 fps while optical testing continued; delivered frames, not a requested mode label, were measured. Source: [unattended test report](UNATTENDED_TEST_REPORT_2026-09-24.md).

## Live Kiyo Pro and LCD: status works, motion is intermittent

The Kiyo Pro was attached to the UNO Q and aimed at the modern display while RetroPie ran FCEUmm. With HDR temporarily disabled, 640-by-480 MJPEG and manual exposure 10 (1 ms) delivered about **59.8-60.2 fps** during the cited live traces. Camera crops changed as the user recentered and moved the camera; normalized regions such as `0.4,0.54,0.055,0.06`, later `0.4,0.30,0.055,0.06`, and eventually `0.205,0.15,0.04,0.05` are evidence of those particular physical placements, not portable settings.

| Live check | Observation | What it establishes |
| --- | --- | --- |
| Gyromite Test | 576 frames in 10 seconds; chosen crop almost continuously green; virtual red light blinked | Sustained Test-field detection at the initial aim |
| Stack-Up Test | 756 frames at 60.2 fps; alternating white/green crop; red light blinked without model motion | Alternating Test recognition at that aim |
| Gyromite Direct | Six spaced game commands, **zero decoded robot actions** | No demonstrated live optical motion in that session |
| Stack-Up Direct, one UP/RIGHT sequence | Both decoded; UP was correctly blocked at maximum lift, RIGHT moved station 3 to 4 | A genuine end-to-end optical success, but only one sequence |
| Stack-Up Direct, later DOWN | Decoded live; virtual lift moved from 6 to 5 | Another genuine optical action |
| Four further hands-free UP/RIGHT cycles | 80 bright camera samples, **zero complete commands**; station remained 3 | The successful sequence was not a dependable play rate |

The camera saw broad status fields much more readily than short cells. An early mixed-brightness score also confused white with green; using green dominance corrected that classification. Later camera traces had all-green or blended runs, or an apparently complete pattern just outside the timing threshold. The strict decoder rejected these instead of guessing a direction. A longer dark idle had initially been counted as a preamble; trimming it recovered RIGHT in offline replay, but subsequent live cycles still missed commands. These are chronological revisions in the archived [live optical report](LIVE_OPTICAL_TEST_2026-09-25.md), not current runtime features.

### Where did the cells go?

RetroArch recorded its rendered 13-frame output while the UNO Q logged camera samples. The source contained exact UP_STACK (`0001011111010`), LEFT (`0001010111010`), DOWN_STACK (`0001010101110`), RIGHT (`0001011101010`), and OPEN words. A small dark patch and wider screen average generally lost or blended the same cells. A horizontal band recovered one UP in offline replay, but three more UP/RIGHT cycles yielded no complete word from any band.

| Source-aligned Stack-Up word | Camera finding | Live action |
| --- | --- | --- |
| First UP_STACK | Active sequence and green ninth bit survived; timing check failed | Rejected |
| LEFT | Active sequence and green ninth bit survived; timing check failed | Rejected |
| Later UP_STACK | Several cells blended into a long green run | Rejected |
| DOWN_STACK | Distinguishable sequence, including dark ninth bit | Decoded; lift 6 to 5 |
| RIGHT | Extra or blended cells prevented unique alignment | Rejected |

The ninth cell was **not always missing**. UP_STACK and RIGHT can differ at one cell, so accepting the nearest word could turn a missed bit into a wrong movement. The source recording proves the game sent a complete message; it does not say the LCD displayed each cell in a way this camera could capture. Source: [live optical report](LIVE_OPTICAL_TEST_2026-09-25.md).

## Uncompressed and row-level Kiyo experiments

The camera enumerated MJPEG, YUYV, NV12, and H264 up to 1920-by-1080 at 60 fps on a 5 Gbit/s USB 3 link. At 1280-by-720 YUYV, delivered capture was about 60 fps, yet a recorded UP/LEFT/UP sequence decoded LEFT and missed both UP words. A standalone 1920-by-1080 raw NV12 benchmark captured 660 frames in 11.9 seconds (**55.5 fps computed from those recorded numbers**); the archived note calls it “around 60 fps.” Full BGR conversion was about 36 fps in that comparison. Uncompressed pixels and faster processing alone did not establish exact command recovery.

The aligned 1080p study disabled OpenCV color conversion and sampled luma plus NV12 V chroma from **three 55-pixel strips × 24 horizontal bands = 72 regions**. Each of two runs captured 1,800 camera frames near 60 fps while RetroArch independently recorded four complete source commands. Each region was allowed a start shift of up to three captured frames for an **offline exact-match** comparison; the fifth key press near shutdown was excluded. Normal framing sampled the upper 510 rows. Digital zoom `180` and upward tilt `36000` expanded the game image to about 900 rows for the second run.

| Framing | Source move | Whole-frame average | Exact regions / 72 |
| --- | --- | --- | ---: |
| Normal | UP_STACK | Exact | 69 |
| Normal | LEFT | Exact | 69 |
| Normal | UP_STACK | `0001011111011` instead of `0001011111010` | 0 |
| Normal | RIGHT | Best alignment differed by two bits | 0 |
| Zoom and tilt | RIGHT | Exact | 69 |
| Zoom and tilt | UP_STACK | Best alignment differed by two bits | 0 |
| Zoom and tilt | LEFT | Best alignment differed by three bits | 0 |
| Zoom and tilt | UP_STACK | Best alignment differed by two bits | 0 |

The third normal-frame pattern happens to be a valid **Gyromite DOWN** word, but is invalid for Stack-Up. A game-specific decoder rejects it; a nearest-pattern decoder would weaken that safety boundary. **No row region recovered any of the five rejected source-aligned commands.** A green top-to-bottom intensity gradient appeared even across repeated green frames and did not identify the missing cells. The row bands were diagnostic only; no row-based action path was deployed.

The separate `/dev/video3` UVC metadata node produced 30 nonempty blocks totaling 660 bytes (22 per block). Its host timestamp intervals had median **16.63 ms**, range **14.22-21.37 ms**, in that short capture. PTS and SCR fields were present. More precise timestamps cannot recreate a light cell absent from captured pixels. The Kiyo zoom, pan, tilt, exposure, and live MJPEG mode were restored after testing. Source: [Kiyo Pro raw-row report](KIYO_PRO_ROW_TEST_2026-09-25.md).

## FCEUmm frame link: complete game words at the source

The next experiment moved observation inside RetroArch. A small libretro wrapper delegates normal play to the installed FCEUmm core, classifies each rendered NES frame as dark, green, or other, and sends its frame index and class to a local Unix socket. The receiver checks the RetroArch sender, wrapper path, exact ROM identity, and consecutive 13-frame word before sending a command to the UNO Q. The UNO Q applies the same bounded virtual model. The wrapper observes rendered light, not hidden game memory or objectives.

| Live RetroPie Direct session | Complete commands recorded | UNO Q result |
| --- | --- | --- |
| Gyromite | DOWN_GYRO, UP_GYRO, LEFT, RIGHT, OPEN, CLOSE | Lift 6 to 4 to 6; station 2 to 1 to 2; hands closed then reopened. Initial OPEN at an already-open grip was correctly blocked. |
| Stack-Up | CLOSE, DOWN_STACK, OPEN, LEFT, UP_STACK, RIGHT | Hands closed and reopened; lift 6 to 5 to 6; station changed. Initial UP at maximum height was correctly blocked. |

Commands came from the configured Player 1 input in real `.7z` launches, not manual model calls. Receiver journals named the decoded words and source frame numbers; the UNO Q Activity Feed and `/api/state` recorded the corresponding action or block. Example frame indices include Gyromite DOWN_GYRO at **3678**, UP_GYRO at **4681**, Stack-Up DOWN_STACK at **12121**, and UP_STACK at **13644**. The first Stack-Up Test-artwork trial revealed that dark borders fooled an overly strict whole-frame green classifier. Sampling the central picture area as well corrected the class sequence. No idle or Test-only frames caused unintended movement in these sessions. The local suite at that stage passed **48 tests**. Source: [FCEUmm frame-link report](FRAME_LINK_TEST_2026-09-25.md).

This is functional end-to-end evidence for six primitives in each game's Direct mode. It is **not** a measured long-session missed-command rate, a Stack-Up Memory/Bingo validation, or proof that the browser knows Hector's position or the game's target pattern.

## Nestopia: second core and Player 2 return

The same wrapper design was built around the installed Nestopia core. An isolated test first recorded Stack-Up Test alternation and exact UP_STACK, plus Gyromite RIGHT, LEFT, and UP_GYRO. Nestopia requested XRGB8888 pixels, which the classifier handled. An initial headless crash also occurred with the unmodified Nestopia core; disabling threaded video in the **test harness** allowed the isolated runs. Normal RetroPie launches then selected the product Nestopia wrapper, accepted its process and ROM identity, and sent Stack-Up LEFT at frame **4328** and Gyromite RIGHT, LEFT, UP_GYRO at **2416**, **2491**, **2566** to the UNO Q. Up was correctly blocked at maximum lift. The temporary overrides and input tap were removed. Source: [Nestopia frame-link report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md).

Gyromite's return path needed its own test. Nestopia treats libretro device `1` as Auto and may connect the game's optical peripheral on Player 2. The wrapper now selects explicit gamepad device `257` after ROM load. These were **screen-observed gate tests**, separate from decoded movement tests:

| Host and core | Blue gate before | During blue hold | After release | During red-only hold |
| --- | --- | --- | --- | --- |
| Batocera FCEUmm, screenshot y pixels | 209-428 | 356-576 | 209-428 | 209-428 |
| Batocera Nestopia, screenshot y pixels | 209-428 | 356-575 | 209-428 | 209-428 |
| RetroPie Nestopia, cyan column x=69 | 40-87 | 64-110, then 72-119 | 40-87 | 40-87 |

The pixel ranges refer to the cited screenshot or NES recording geometry; they are **not comparable travel distances across hosts**. They show an isolated blue press, its release, and a red-only negative control. Earlier player-observed RetroPie FCEUmm red and blue gate checks also passed. The [release validation](RELEASE_VALIDATION_0.1.0.md) records Batocera input mapping, installer, and reboot checks; the [Nestopia report](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md) records its corrective wrapper test.

## Evidence boundary and open work

The measured camera/LCD path recognized Test fields and occasionally complete movement words, but repeatedly missed commands after recentering, wider sampling, uncompressed capture, row analysis, and zoom. These tests do **not** prove that no camera could ever read the original signal. They establish that the tested Kiyo Pro, display, modes, and 60 fps timing did not support dependable autonomous play. The frame link removed that sampling boundary and delivered complete Direct-mode words from both games under FCEUmm; Nestopia delivered movement in both games and a verified Gyromite blue-gate return.

Remaining evidence gaps are long unattended sessions with a measured missed-command rate, full six-command Nestopia runs in every game mode, Stack-Up Memory and Bingo cadence and starting layouts, alternate video filters/palettes, full-game outcomes, other Batocera hardware, and complete direct visual checks of every UNO Q matrix animation. A selected game, fresh frame link, decoded word, accepted model action, and visible in-game gate response should continue to be reported as **separate milestones**.

### Detailed records

- [Unattended optical simulation and two-game model checks](UNATTENDED_TEST_REPORT_2026-09-24.md)
- [Live Kiyo Pro optical field tests and source-aligned commands](LIVE_OPTICAL_TEST_2026-09-25.md)
- [Raw NV12 row experiment and UVC timing metadata](KIYO_PRO_ROW_TEST_2026-09-25.md)
- [FCEUmm frame-link Direct-mode verification](FRAME_LINK_TEST_2026-09-25.md)
- [Nestopia isolated, live, and gate-return verification](NESTOPIA_FRAME_LINK_TEST_2026-09-25.md)
- [Release candidate platform and input checks](RELEASE_VALIDATION_0.1.0.md)
- [ROM command derivation and exact patterns](ROM_SIGNAL_ANALYSIS.md)

## Subsequent shared Router validation

The measurements and frame indices in this report belong to the dated optical and libretro experiments. Current installations add shared Matrix ownership and boot-bound input leases. The [verification plan](VERIFICATION_PLAN.md#shared-router-follow-up--27-september-2026) records later player-confirmed games and automated web/chooser checks. On 28 September, session routing passed automated source reconnect tests on RetroArch 1.19.1 and a separate 1.20.0 build; physical wireless endurance testing remains outstanding. The shared Controller Router repository's `docs/ROUTING_VALIDATION.md` records that evidence. These follow-up checks do not revise the original optical measurements or establish new missed-command rates.
