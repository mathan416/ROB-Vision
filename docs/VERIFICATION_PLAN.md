# R.O.B. Vision verification plan

**Current evidence:** the preview, UNO Q app, real Gyromite launch and exit identification, live red/blue pad press/release events at RetroPie's input device, and a user-observed Game A gate response have been verified. Optical decoding with a camera remains to be tested.

| Gate | Test | Pass condition | Status |
| --- | --- | --- | --- |
| Gyromite preview | Run the unspun one-gate press, dual relay, spin-down recovery, and cleanup | Pad states stay independent; after one recovery per gyro, both gyros return upright to holders, buttons release, and COMPLETE remains stable | Browser preview observed. |
| Preview reset | Use Home and demo restart at different phases | Timers, queue, pieces, and buttons return to initial state | Browser implementation; verify after changes. |
| Stack-Up preview | Move red alone, then blue and white together; try a blocked release | Five discs conserved, colors stay ordered, and invalid moves leave state unchanged | Browser observed; five model tests pass. |
| Optical capture | Use actual game Test mode on intended LCD/OLED | Complete command decoded with timestamp evidence; idle produces no false command | Not run. |
| Game identity | Launch exact configured Gyromite/Stack-Up names and unknown titles | Correct context on start; idle on exit/unknown | Real Gyromite `.7z` launch and exit selected then cleared UNO Q context. Both games' installed hooks passed controlled start/end tests. Unknown title and real Stack-Up launch remain pending. |
| Gyromite LAN output | Send red/blue virtual states and disconnect | Correct Controller 2 mapping; button releases on virtual lift, timeout, exit, and reset | Both colors pressed/released at Linux input with Player 2 forced to Gamepad. Initial isolated red moved the blue gate. After swapping A/B and restarting, isolated blue moved the blue gate and released it. Red gate and sustained link-loss observation remain pending. |
| Multi-client UI | Open laptop, iPad, and phone simultaneously | Same UNO Q snapshot and ordered events; reconnection does not reset game | Not run. |
