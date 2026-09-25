# R.O.B. Vision safety and security

R.O.B. and every accessory are virtual. There are no motors or physical gyros. The relevant risks are incorrect game input, stale network state, untrusted browser access, and camera privacy.

- Mission and Setup browser controls intentionally work without a token on the trusted LAN. Keep ports 80 and 8766 away from guest and public networks. Browser writes use same-origin JSON checks; this is not a substitute for network isolation.
- RetroPie launch notices and receiver identity require the shared controller token. Pairing uses a short-lived code and checked TLS certificate fingerprint. Do not publish the token or include it in logs.
- The optical decoder rejects incomplete and ambiguous flashes. A camera dropout does not repeat the last action. Actual display/camera performance remains unverified.
- Virtual movement validates bounds and block conservation. Invalid Stack-Up transfers do not move pieces.
- The RetroPie receiver releases both Gyromite buttons on exit, unknown game, missing process, or 750 ms without a good response. Fast Gate holds expire after 60 seconds.
- Live **Emergency Stop** stops camera capture and clears game selection. In the offline preview it only cancels the local animation. It is not a physical power switch.
- The camera preview is a low-rate framing aid on Setup. The app does not record camera video by default. Avoid aiming it at unrelated private content. User ROMs are not bundled.

The original booklet's warnings about a physical spinning gyro are historical context for Nintendo's toy, not a hazard from this virtual implementation.
