# R.O.B. Vision troubleshooting

**Current preview is local simulation.** It does not require an UNO Q, camera, game host, or network pairing.

| Symptom | Check |
| --- | --- |
| Dashboard does not open | Serve the project directory locally and visit `/dashboard/`; check the server address and browser console. |
| Demo appears stuck | Select **Home**, then **Run Demo Sequence**. Gyromite includes a long illustrative spin-down, one recovery for each gyro, and holder cleanup before it stops. |
| Red or blue indicator reads RELEASED | The virtual gyro is off that pad, has tipped, or R.O.B. lifted it. The unspun one-gate example presses only while held down. |
| Stack-Up shows old Gyromite pieces | Select **Stack-Up** in Accessory Bay; refresh if a previous page version was cached. |
| Stop button disables controls | Select **Reset Stop**; it resets the local simulation. |

## Planned UNO Q diagnostics

1. **Game not identified:** check the exact configured ROM basename and launch/exit event. Unknown titles select idle.
2. **No optical command:** inspect camera framing, exposure, timestamped flash trace, and game Test mode. An incomplete message never moves virtual R.O.B.
3. **Virtual R.O.B. does not act:** check accepted command, current mode, busy state, and object-transition rejection log.
4. **Gyromite gate does not respond:** compare virtual red/blue pad state, fresh LAN packet, paired receiver state, A/B mapping, and emulator controller assignment in that order.
5. **Browser shows stale state:** reconnect for a fresh UNO Q snapshot; do not guess position from an old animation.
6. **Return link fails:** both virtual buttons should release; repair pairing or network freshness before continuing.

On the dedicated test setup, check the UNO Q panel at `http://arduiain.local` and the RetroPie receiver with `systemctl status rob-vision-controller2.service`. The virtual pad should appear as `/dev/input/js1` while the existing player controller remains `/dev/input/js0`. If the game context remains selected after exit, rerun the installed `runcommand-onend.sh` hook and inspect `/dev/shm/runcommand.log` for a timeout. Preserve timestamps and event sequences when reporting an issue, but do not include pairing secrets or ROM files.
