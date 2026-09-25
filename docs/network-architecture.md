# R.O.B. Vision network architecture

The UNO Q owns virtual R.O.B. state. A browser on the trusted LAN renders it, and RetroPie supplies game identity and receives Gyromite pad states. The game display sends optical flashes to the UNO Q camera; no USB game-data tether is used.

```text
RetroPie runcommand ── authenticated launch/exit HTTP ──> UNO Q
RetroPie receiver <── authenticated /api/state polling ── UNO Q virtual pads
Browser <── /api/state every 500 ms ── UNO Q controller
Game screen ── optical flashes ──> UNO Q camera (hardware validation pending)
```

The App Lab gateway serves `http://arduiain.local` on port 80 and forwards to the controller on 8766. Existing Avahi supplies the `.local` name. Wi-Fi or an Ethernet adapter carries the same HTTP traffic. The Ethernet adapter shares the current USB hub; the supplied but uninstalled host recovery helper refuses a whole-hub reset while Ethernet is attached.

## Identity and safety

Exact configured RetroPie ROM basenames select `gyromite` or `stack_up`; unknown titles clear context. The launch notifier and receiver poll use the shared token. Pairing sends that token to RetroPie after checking a short-lived code and TLS certificate fingerprint. Browser controls intentionally require no token on the trusted LAN, so neither port should be exposed publicly.

The receiver is a root uinput service that polls about every 50 ms. It releases both buttons after 750 ms without a good response, on game exit, or when no matching RetroArch process is active. It scans the running process and can resynchronize game identity after a UNO Q restart. Its authenticated poll also supplies the online indicator, which expires after three seconds.

The UNO Q's `/api/state` response is a schema-versioned snapshot with recent events. There is no push stream, durable event log, sequence protocol, or receiver acknowledgement of an on-screen gate animation. Browser refresh gets the current state. The camera preview on Setup is a low-rate framing aid and is not recorded by default. An emulator command hook remains unimplemented.
