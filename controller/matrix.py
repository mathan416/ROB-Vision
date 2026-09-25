"""Best-effort UNO Q LED matrix bridge for R.O.B. Vision."""

from enum import IntEnum
from time import monotonic


class MatrixMode(IntEnum):
    LOADING = 0
    IDLE = 1
    GYROMITE = 2
    STACK_UP = 3
    TEST = 4
    TEST_FLASH = 5
    PAIRING = 6
    FAULT = 7
    OFF = 8


HINTS = {"LEFT": 1, "RIGHT": 2, "UP": 3, "DOWN": 4, "OPEN": 5, "CLOSE": 6}


class MatrixDisplay:
    """Send authoritative state and fresh action hints; keep absence nonfatal."""

    def __init__(self, call=None):
        if call is None:
            try:
                from arduino.app_utils import Bridge
                call = Bridge.call
            except ImportError:
                pass
        self.call = call
        self.last_mode = None
        self.last_sequence = -1
        self.last_sent = 0.0
        self.retry_at = 0.0
        self.pairing_until = 0.0
        self.last_error = None

    def show_pairing(self, seconds=300):
        self.pairing_until = monotonic() + seconds

    def clear_pairing(self):
        self.pairing_until = 0.0

    def send(self, mode, hint=0, force=False):
        now = monotonic()
        if not self.call or now < self.retry_at:
            return False
        if not force and mode == self.last_mode and not hint and now - self.last_sent < 1.0:
            return True
        try:
            self.call("set_rob_display", int(mode), int(hint))
        except Exception as exc:  # App Lab bridge errors differ across releases.
            self.last_error = str(exc)
            self.retry_at = now + 1.0
            return False
        self.last_mode = mode
        self.last_sent = now
        self.last_error = None
        return True

    def update(self, snapshot):
        if monotonic() < self.pairing_until:
            mode = MatrixMode.PAIRING
        elif snapshot["test"]["armed"]:
            mode = MatrixMode.TEST_FLASH if snapshot["test"]["flash_active"] else MatrixMode.TEST
        elif snapshot["game"] == "gyromite":
            mode = MatrixMode.GYROMITE
        elif snapshot["game"] == "stack_up":
            mode = MatrixMode.STACK_UP
        else:
            mode = MatrixMode.IDLE

        hint = 0
        if snapshot["sequence"] != self.last_sequence:
            self.last_sequence = snapshot["sequence"]
            if mode in (MatrixMode.GYROMITE, MatrixMode.STACK_UP):
                recent = snapshot["events"][-1] if snapshot["events"] else None
                if recent and recent["kind"] == "action":
                    command = (recent.get("command") or "").split("_", 1)[0]
                    hint = HINTS.get(command, 0)
        return self.send(mode, hint)

    def run(self, snapshot, stop_event):
        while not stop_event.wait(.3):
            self.update(snapshot())
        self.send(MatrixMode.OFF, force=True)

    def status(self):
        return {"available": self.call is not None,
                "bridge_ok": self.last_sent > 0 and monotonic() - self.last_sent < 3 and self.last_error is None,
                "mode": self.last_mode.name.lower() if self.last_mode is not None else None}
