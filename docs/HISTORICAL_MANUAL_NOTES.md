# Original R.O.B. manual: historical notes

**Source:** [R.O.B. instruction manual transcript](https://www.atarihq.com/tsr/manuals/robmanual.txt) at Atari HQ. This is a paraphrased reading of the original physical toy, not a hardware specification for R.O.B. Vision.

The original robot grasped/released, raised/lowered, and rotated/carried objects. Its operator aimed its eyes at a CRT test signal. A head light indicated optical reception and readiness, went out while it moved, and returned when ready for another command. R.O.B. Vision represents those movements and states in a browser; a paired RetroPie or supported Batocera console passes rendered game frames to the UNO Q.

The manual warns about glare, fluorescent light, blocked sight lines, overlays, and overly bright images. Those are historical concerns for the physical robot. The virtual UI separates **game frames linked** from **complete command decoded** and shows `TEST → READY → BUSY → READY` clearly. The original CRT distance is only historical context.

The original manual's battery, mechanical, and spinning-gyro safety instructions apply to Nintendo's toy. This virtual project instead needs robust command validation, correct virtual piece state, a fresh paired Gyromite return link, and clear simulation/live labels. See [optical input](optical-input.md) and the [virtual system contract](VIRTUAL_SYSTEM.md).
