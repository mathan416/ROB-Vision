# Original R.O.B. manual: historical notes

**Source:** [R.O.B. instruction manual transcript](https://www.atarihq.com/tsr/manuals/robmanual.txt) at Atari HQ. This is a paraphrased reading of the original physical toy, not a hardware specification for R.O.B. Vision.

The original robot grasped/released, raised/lowered, and rotated/carried objects. Its operator aimed its eyes at a CRT test signal. A head light indicated optical reception and readiness, went out while it moved, and returned when ready for another command. R.O.B. Vision represents those movements and states in a browser; its UNO Q camera is separately mounted and watches a modern LCD/OLED. There is no physical R.O.B. head, arm, or accessory.

The manual warns about glare, fluorescent light, blocked sight lines, overlays, and overly bright images. Those remain useful camera-test cases. The modern UI must separate **flash visible** from **complete command decoded**, and show `TEST → READY → BUSY → READY` clearly. The original approximate CRT distance is only historical context; actual camera framing and exposure need calibration on the chosen display.

The original manual's battery, mechanical, and spinning-gyro safety instructions apply to Nintendo's toy. This virtual project instead needs robust command validation, correct virtual piece state, a fresh paired Gyromite return link, and clear simulation/live labels. See [optical input](optical-input.md) and the [virtual system contract](VIRTUAL_SYSTEM.md).
