# R.O.B. Vision third-party components and rights

The project includes an App Lab Python service and matrix sketch, original dashboard SVG/CSS art, Python controller code, deployment helpers, and generated guides. It contains no Nintendo ROM, game artwork, or Robert project code.

| Item | Use and status | Rights / source |
| --- | --- | --- |
| DM Sans and Barlow Condensed | Bundled dashboard/PDF fonts | SIL Open Font License files in `dashboard/fonts/`. |
| OpenCV (`requirements-camera.txt`) | Optional camera capture dependency; present in the tested App Lab image | Installed separately from repository source. |
| ReportLab | Builds printable PDF guides from Markdown | Build-time dependency, not a game runtime dependency. |
| Arduino UNO Q App Lab and Router Bridge | Hosts controller and LED matrix sketch | Platform dependency; vendor files are not redistributed here. |
| VirtualGlove host-helper patterns | R.O.B. Vision versions of camera recovery, shutdown, early start, and network status | Adapted from the user's MIT-licensed VirtualGlove project; see `deploy/uno-q/README.md`. |
| Nintendo R.O.B., Gyromite, Stack-Up | Historical inspiration and compatibility targets | Nintendo marks and assets remain with their owner. |
| Atari HQ and Digital Press manuals | Paraphrased research references | Linked in the manual-notes guides; text and scans are not bundled. |
| Aluminite Robert simulator | Behavioral research only | No GPL-3.0 code or assets imported. |
| User-supplied ROMs | Analysis and play on the user's machines | Remain outside this repository and release bundle. |

Check dependency versions and license inventory again before packaging a redistributable release.
