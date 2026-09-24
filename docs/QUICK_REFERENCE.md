# R.O.B. Vision quick reference

**R.O.B. is virtual.** The UNO Q dashboard and RetroPie Gyromite Controller 2 link are running. The blue gate was observed responding in Game A. UNO Q camera capture and a separate red gate check remain to be verified.

## Preview controls

| Control | Result |
| --- | --- |
| Gyromite / Stack-Up / Pose Lab | Choose a game accessory scene or R.O.B.'s motion sandbox. |
| Run Demo Sequence | Start a finite animation. Gyromite ends with both gyros stored; Stack-Up moves red alone, then blue and white together. |
| Stack-Up Commands | Apply one local virtual turn, height change, open, or close; valid actions update the disc stacks. |
| Pose Preview | Try R.O.B.'s movement locally in Gyromite or Pose Lab. |
| Home | Reset all virtual pieces, buttons, pose, and timers. |
| Emergency Stop / Reset Stop | Cancel or re-enable the local simulation. |

## Fast Gates during live Gyromite

Open `http://arduiain.local/dashboard/`. **Lower Blue** or **Lower Red** presses that gate immediately; tap it again to raise it. **Release Both** raises both. Keyboard: **2** blue, **1** red, **0** release both. Each press releases after 60 seconds, and leaving the game releases both. The controls appear when Gyromite is selected and camera capture is stopped. Use **Home** first if a gyro has been moved with the regular controls.

## Planned connected loop

```text
cabinet game flash → UNO Q camera → validated command → virtual R.O.B. + pieces
                                              ↓
                          browser on laptop / iPad / phone
Gyromite virtual pad state → Wi-Fi/Ethernet → game-host Controller 2 receiver
```

An unspun gyro held on one pad can press one gate. A spinning gyro remains on a pad while R.O.B. operates the other. When no longer needed, gyros return to holders. The preview's 55-second spin timer is illustrative. A lost game link releases both virtual buttons.

**SIMULATION / GAME LINK OFFLINE** means no game is connected. **NO SIGNAL** or **UNREADABLE SIGNAL** will mean no virtual action in the planned camera mode. See the [user guide](USER_GUIDE.md) and [virtual system contract](VIRTUAL_SYSTEM.md).
