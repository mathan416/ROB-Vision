# R.O.B. Vision network architecture

The UNO Q owns Buddy's virtual pose and game pieces. A browser on the trusted LAN renders the state. A paired RetroPie or supported Batocera console identifies the running game, sends commands decoded from rendered NES frames, and receives Gyromite's virtual Controller 2 button states.

```text
Console launch hook ── authenticated launch/exit HTTP ──> UNO Q
Console receiver <── authenticated /api/state polling ── UNO Q virtual pads
Browser <── /api/state every 500 ms ── UNO Q controller
FCEUmm/Nestopia frames ── local verified socket ──> console receiver
Console receiver ── authenticated command HTTP ──> UNO Q model
```

The App Lab gateway serves `http://arduiain.local` on port 80 and forwards to the controller on 8766. Existing Avahi supplies the `.local` name. Wi-Fi or an Ethernet adapter carries the same HTTP traffic. The Ethernet adapter shares the current USB hub.

## Identity and safety

Exact configured ROM basenames select `gyromite` or `stack_up`; unknown titles clear context. The launch notifier, receiver poll, and game-frame command POST use the paired console's credential. Pairing sends that credential to the console after checking a short-lived code and TLS certificate fingerprint. If both consoles are paired, the UNO Q accepts game commands only from the active game's console. Browser controls intentionally require no token on the trusted LAN, so neither port should be exposed publicly.

The receiver is a root uinput service that polls about every 50 ms. It releases both buttons after 750 ms without a good response, on game exit, or when no matching RetroArch process is active. It scans the running process and can resynchronize game identity after a UNO Q restart. Its authenticated poll also supplies the online indicator, which expires after three seconds.

The UNO Q's `/api/state` response is a schema-versioned snapshot with recent events. There is no push stream, durable event log, sequence protocol, or receiver acknowledgement of an on-screen gate animation. Browser refresh gets the current state. The console frame link reports its fresh activity in `/api/state.input.frame_hook`.
