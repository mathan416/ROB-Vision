# UNO Q host helpers for R.O.B. Vision

These are R.O.B. Vision counterparts of the supplied VirtualGlove units. They are **host** files for the UNO Q, outside the App Lab container. Their paths and service names are separate from VirtualGlove.

| Files | Role |
| --- | --- |
| `rob-vision-system-shutdown.path`, `.service`, `.conf` | Consume a shutdown request and ask systemd to halt the UNO Q. This is a host capability only; R.O.B. Vision currently has no shutdown button or request writer. |
| `rob-vision-early-start.service`, `rob-vision-early-start.py` | Optional early release of a verified R.O.B. Vision sketch image. The helper checks the UNO Q model, configured startup app, sketch image, and flashed code samples before writing the release flag. Normal App Lab startup remains authoritative. |
| `rob-vision-wifi-status.py`, `.service`, `.timer` | Publish read-only Wi-Fi and Ethernet link state and directed broadcast addresses every five seconds to the R.O.B. Vision data directory. No network names or credentials are published. |

The device's `.local` name comes from its hostname and Avahi mDNS service. Controller Router serves the entry page on port 80; R.O.B. Vision serves its browser pages on port 8101 and receiver API on port 8766. Both products use the same device hostname or any reachable LAN IP address. R.O.B. Vision does not register a separate mDNS name. The installer prints both address forms after a successful start. `virtualglove.local` was verified serving the dashboard at `10.0.2.84` and `10.0.2.86`; `arduiain.local` is another tested UNO Q. The optional Wi-Fi status timer observes link health; it does not register or repair mDNS. The sampler was run once on the `arduiain.local` UNO Q as the unprivileged `arduino` user and reported connected networking with a directed broadcast address. Its service and timer are not installed or enabled yet.

The shutdown service has its own `.shutdown-enabled` marker and `shutdown-request` file. There is deliberately no browser endpoint that writes a shutdown request.

These files are source-controlled and tested locally, but the R.O.B. Vision host units have **not** been installed on `arduiain.local`: that host requires an interactive `sudo` password. The existing VirtualGlove services remain untouched. These product-specific early-start files are for legacy standalone maintenance. Do not enable them on a shared installation: Controller Router is the startup app and sole Matrix firmware owner.
