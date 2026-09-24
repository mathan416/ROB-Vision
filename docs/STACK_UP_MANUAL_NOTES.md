# Stack-Up manual: design and test notes

**Source:** [Stack-Up instruction booklet scan](https://www.digitpress.com/library/manuals/nes/Stack-up.pdf) at Digital Press. This paraphrases the original accessory and game rules. R.O.B. Vision models the robot and pieces virtually; no physical tray or disc is built.

## Virtual set and starting layouts

The booklet shows five colored ring-shaped pieces—red, white, blue, yellow, and green—on five numbered trays around R.O.B. Tray 3 is directly in front. Direct and Memory begin with all five on Tray 3, top to bottom red, white, blue, yellow, green. One-player Bingo also begins with five on Tray 3, in any color order. Two-player Bingo begins with three on Tray 3 and one each on Trays 2 and 4. These layouts become UNO Q virtual-state profiles, with matching browser graphics. At the start of a virtual session, the pose is centered over Tray 3, at the highest level, with hands open.

## Command and stack behavior

The game sends one of six movement commands—left, right, up, down, open, close—per completed signal. The original robot has five tray stations and six height levels; Stack-Up up/down moves one level, unlike Gyromite's two-level movement. Closing at a lower disc can lift that disc and every disc stacked above it together. The virtual controller therefore carries an ordered **stack segment**, not just one disc. Opening places that segment, preserving color order; all five discs remain accounted for. The game does not send a disc ID, destination tray, target pattern, or confirmation that the player's arrangement is correct. Those are inferred from our virtual pose and stack state or seen by the player on the game screen.

The current scripted preview applies one virtual command per step. It first moves red alone from Tray 3 to Tray 4, then closes around blue at level 3 and carries blue plus white to Tray 2. The discs keep their bottom-to-top order, and all five remain accounted for. Local command buttons use the same virtual stack model. This is not evidence that the camera decoded any command; live play must animate each received primitive independently, including repeated commands and Memory playback.

## Modes

| Mode | Booklet behavior | Virtual design implication |
| --- | --- | --- |
| Test | Optical aiming signal | Reuse camera calibration and readiness check. |
| Direct | Professor lands on six command keys | Decode and display left, right, up, down, open, or close. Player scores/advances with Start after arrangement. |
| Memory | Up to 100 programmed commands at selected speed, then `END` | Measure cadence; bound queued virtual actions and report misses. `END` is a programming marker, not a robot movement flash. |
| Bingo, one player | Row or column completion sends a command | Apply only a complete validated optical command. |
| Bingo, two players | Two human controllers and a different starting layout | Validate separately; keep human controller input on the cabinet. |

The booklet says a simultaneous completed row and column is a no-command condition until one line changes. Do not turn that pattern into two virtual actions. The flash stream does not report a target pattern or a victory result. The UNO Q knows its own modeled disc stacks but cannot infer the game's scoring outcome without another source. In Direct, Memory, and one-player Bingo, the human presses Start to request scoring after matching the displayed arrangement; a successful animation alone does not advance a round.

Stack-Up's documented modes have no Gyromite-style accessory that presses Controller 2. Its tray model needs no button return path to the game. The browser preview now demonstrates both a one-disc transfer and an ordered two-disc carry. Future optical play must conserve all five discs, update one modeled placement per valid open command, and handle Memory timing without silent command loss.

See the [virtual system contract](VIRTUAL_SYSTEM.md), [ROM signal analysis](ROM_SIGNAL_ANALYSIS.md), and [verification plan](VERIFICATION_PLAN.md).
