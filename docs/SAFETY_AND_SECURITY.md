# R.O.B. Vision safety and security

The relevant risks are incorrect game input, stale network state, and untrusted browser access.

- Mission and Setup browser controls intentionally work without a token on the trusted LAN. Keep Router port 80, browser port 8101, and receiver port 8766 away from guest and public networks. Browser writes use same-origin JSON checks; this is not a substitute for network isolation.
- Console launch notices, receiver identity, and emulator-frame commands require the paired console credential. Pairing uses a short-lived code and checked TLS certificate fingerprint. Do not publish credentials or include them in logs.
- The game-frame decoder rejects incomplete and ambiguous patterns. The console frame link also requires a complete 13-frame pattern, matching ROM identity, and verified local sender credentials. Missing or malformed frame data does not repeat the last action.
- Virtual movement validates bounds and block conservation. Invalid Stack-Up transfers do not move pieces.
- The console receiver releases both Gyromite buttons on exit, unknown game, missing process, or 750 ms without a good response. Fast Gate holds expire after 60 seconds.
- Live **Emergency Stop** clears game selection and releases virtual pads. In the offline preview it only cancels the local animation.
- User ROMs are not bundled.

Controller Router grants one boot-bound, short-lived input lease. Managed apps reject missing or expired leases and release input on loss. Console player assignments and enabled systems are edited through authenticated product APIs; saves and rollback are blocked during a Libretro game. Router runtime never rewrites saved RetroArch configuration.
