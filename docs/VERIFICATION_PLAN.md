# R.O.B. Vision verification plan

**Current evidence:** the browser preview demonstrates art, scripted virtual motion, independent gyro timers, virtual pad indicators, one recovery per gyro, and finite cleanup. It does not validate optical decoding, UNO Q hosting, LAN return input, or game behavior.

| Gate | Test | Pass condition | Status |
| --- | --- | --- | --- |
| Gyromite preview | Run the unspun one-gate press, dual relay, spin-down recovery, and cleanup | Pad states stay independent; after one recovery per gyro, both gyros return upright to holders, buttons release, and COMPLETE remains stable | Browser preview observed. |
| Preview reset | Use Home and demo restart at different phases | Timers, queue, pieces, and buttons return to initial state | Browser implementation; verify after changes. |
| Stack-Up preview | Move red alone, then blue and white together; try a blocked release | Five discs conserved, colors stay ordered, and invalid moves leave state unchanged | Browser observed; five model tests pass. |
| Optical capture | Use actual game Test mode on intended LCD/OLED | Complete command decoded with timestamp evidence; idle produces no false command | Not run. |
| Game identity | Launch exact configured Gyromite/Stack-Up names and unknown titles | Correct context on start; idle on exit/unknown | Local resolver tested; live hook not installed. |
| Gyromite LAN output | Send red/blue virtual states and disconnect | Correct Controller 2 mapping; button releases on virtual lift, timeout, exit, and reset | Not run. |
| Multi-client UI | Open laptop, iPad, and phone simultaneously | Same UNO Q snapshot and ordered events; reconnection does not reset game | Not run. |
