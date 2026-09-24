# R.O.B. Vision safety and security

R.O.B. and its accessories are virtual. This project has no robot arm, powered gripper, physical spinner, tray sensor, or actuator supply. The dashboard **Emergency Stop** cancels a local animation; it does not cut physical power. The main risks are incorrect game input, stale network state, camera privacy, and misleading UI status.

- Reject incomplete or ambiguous optical commands. A flicker or camera dropout must not repeat the last action.
- Bound every virtual pose and object transfer. A disc cannot appear on two trays, and one gyro cannot occupy two stations.
- The UNO Q, not a browser tab, owns virtual state and Gyromite pad output in the planned connected system.
- Pair the Gyromite sender and receiver on a trusted LAN. Version and authenticate messages, reject stale sequences, and release both Controller 2 buttons on timeout, exit, reset, or unpairing.
- Show simulation, optical validity, and game-link state separately. A drawn gyro on a pad is not proof that the emulator received its button state.
- Restrict camera diagnostics to trusted clients. Keep the game-screen camera aligned only to the intended display; do not record video by default. Do not package user ROMs in logs or releases.
- Browser clients reconnect from a snapshot. They do not resume a partially accepted action or silently assert old button states.

The original Gyromite booklet's warnings about touching a real spinning gyro describe Nintendo's physical toy. They are historical context, not a hardware hazard in this virtual implementation.
