# R.O.B. Vision safety and security

R.O.B. and every accessory are virtual. There are no motors or physical gyros. The relevant risks are incorrect game input, stale network state, untrusted browser access.

- Mission and Setup browser controls intentionally work without a token on the trusted LAN. Keep ports 80 and 8766 away from guest and public networks. Browser writes use same-origin JSON checks; this is not a substitute for network isolation.
- RetroPie launch notices, receiver identity, and emulator-frame commands require the shared controller token. Pairing uses a short-lived code and checked TLS certificate fingerprint. Do not publish the token or include it in logs.
- The optical decoder rejects incomplete and ambiguous flashes. The RetroPie frame link also requires a complete 13-frame pattern, matching ROM identity, and verified local sender credentials. Missing or malformed frame data does not repeat the last action.
- Virtual movement validates bounds and block conservation. Invalid Stack-Up transfers do not move pieces.
- The RetroPie receiver releases both Gyromite buttons on exit, unknown game, missing process, or 750 ms without a good response. Fast Gate holds expire after 60 seconds.
- Live **Emergency Stop** clears game selection and releases virtual pads. In the offline preview it only cancels the local animation. It is not a physical power switch.
- User ROMs are not bundled.

The original booklet's warnings about a physical spinning gyro are historical context for Nintendo's toy, not a hazard from this virtual implementation.
