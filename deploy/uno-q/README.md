# UNO Q host helpers for R.O.B. Vision

These are R.O.B. Vision counterparts of the supplied VirtualGlove units. They are **host** files for the UNO Q, outside the App Lab container. Their paths and service names are separate from VirtualGlove.

| Files | Role |
| --- | --- |
| `rob-vision-system-shutdown.path`, `.service`, `.conf` | Consume a shutdown request and ask systemd to halt the UNO Q. This is a host capability only; R.O.B. Vision currently has no shutdown button or request writer. |
| `rob-vision-early-start.service`, `rob-vision-early-start.py` | Optional early release of a verified R.O.B. Vision sketch image. The helper checks the UNO Q model, configured startup app, sketch image, and flashed code samples before writing the release flag. Normal App Lab startup remains authoritative. |
| `rob-vision-wifi-status.py`, `.service`, `.timer` | Publish read-only Wi-Fi and Ethernet link state and directed broadcast addresses every five seconds to the R.O.B. Vision data directory. No network names or credentials are published. |

The device's `.local` name comes from its hostname and Avahi mDNS service. Controller Router serves the entry page on port 80; R.O.B. Vision serves its browser pages on port 8101 and receiver API on port 8766. Both products use the same device hostname or any reachable LAN IP address. R.O.B. Vision does not register a separate mDNS name. The installer prints both address forms after a successful start. The optional network-status sampler observes link health; it does not register or repair mDNS. These product-specific helpers are not installed by the normal shared installer. Inspect the host’s enabled units before enabling an optional helper.


The shutdown service has its own `.shutdown-enabled` marker and `shutdown-request` file. There is deliberately no browser endpoint that writes a shutdown request.

These product-specific early-start files are for legacy standalone maintenance. Do not enable them on a shared installation: Controller Router is the startup app and sole Matrix firmware owner.
