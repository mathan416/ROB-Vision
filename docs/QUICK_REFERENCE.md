# R.O.B. Vision quick reference

**R.O.B. is virtual.** A local controller and optional camera path are available for trials; UNO Q capture timing and Gyromite game feedback are not yet verified. The browser preview is also available.

## Preview controls

| Control | Result |
| --- | --- |
| Gyromite / Stack-Up / Pose Lab | Choose a game accessory scene or R.O.B.'s motion sandbox. |
| Run Demo Sequence | Start a finite animation. Gyromite ends with both gyros stored; Stack-Up moves red alone, then blue and white together. |
| Stack-Up Commands | Apply one local virtual turn, height change, open, or close; valid actions update the disc stacks. |
| Pose Preview | Try R.O.B.'s movement locally in Gyromite or Pose Lab. |
| Home | Reset all virtual pieces, buttons, pose, and timers. |
| Emergency Stop / Reset Stop | Cancel or re-enable the local simulation. |

## Planned connected loop

```text
cabinet game flash → UNO Q camera → validated command → virtual R.O.B. + pieces
                                              ↓
                          browser on laptop / iPad / phone
Gyromite virtual pad state → Wi-Fi/Ethernet → game-host Controller 2 receiver
```

An unspun gyro held on one pad can press one gate. A spinning gyro remains on a pad while R.O.B. operates the other. When no longer needed, gyros return to holders. The preview's 55-second spin timer is illustrative. A lost game link releases both virtual buttons.

**SIMULATION / GAME LINK OFFLINE** means no game is connected. **NO SIGNAL** or **UNREADABLE SIGNAL** will mean no virtual action in the planned camera mode. See the [user guide](USER_GUIDE.md) and [virtual system contract](VIRTUAL_SYSTEM.md).
