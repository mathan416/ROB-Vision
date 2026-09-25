# UNO Q host helpers for R.O.B. Vision

These are R.O.B. Vision counterparts of the supplied VirtualGlove units. They are **host** files for the UNO Q, outside the App Lab container. Their paths and service names are separate from VirtualGlove.

| Files | Role |
| --- | --- |
| `rob-vision-camera-recovery.py`, `.path`, `.service`, `.conf` | Enroll one USB camera, consume a request from the app data directory, and publish a result. It prefers an enrolled camera-port power cycle and refuses a whole-hub reset if the hub also carries Ethernet. |
| `rob-vision-system-shutdown.path`, `.service`, `.conf` | Consume a shutdown request and ask systemd to halt the UNO Q. This is a host capability only; R.O.B. Vision currently has no shutdown button or request writer. |
| `rob-vision-early-start.service`, `rob-vision-early-start.py` | Optional early release of a verified R.O.B. Vision sketch image. The helper checks the UNO Q model, configured startup app, sketch image, and flashed code samples before writing the release flag. Normal App Lab startup remains authoritative. |

The camera helper expects `/home/arduino/ArduinoApps/rob-vision/data/`. A successful installation places its Python file at `/usr/local/libexec/rob-vision-camera-recovery`, the units in `/etc/systemd/system/`, the tmpfiles rules in `/etc/tmpfiles.d/`, and the enrollment at `/etc/rob-vision-camera-recovery.json`. `uhubctl` is needed only for camera-port power cycling. The helper can defer enrollment until a camera is present. The current Setup page's **Reconnect Camera** action retries OpenCV capture; it does not yet write `camera-recovery-request`, so installing these files alone does not activate USB recovery from that button.

The two request types are `enroll` and `recover`. A root-owned camera service consumes `camera-recovery-request` and writes `camera-recovery-result` with `schema`, `status`, and optionally `method`. The readiness marker `.camera-recovery-enabled` is created by the tmpfiles rule. The shutdown service has its own `.shutdown-enabled` marker and `shutdown-request` file. There is deliberately no browser endpoint that writes a shutdown request.

These files are source-controlled and tested locally, but have **not** been installed on `arduiain.local`: that host requires an interactive `sudo` password, and no camera is attached yet. The existing VirtualGlove services remain untouched. Do not enable the optional early-start service until its read-only verification has been run against the installed sketch on the UNO Q.
