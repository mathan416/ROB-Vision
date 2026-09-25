"""Decode exact ROM-derived R.O.B. light cells from rendered NES frames."""

from collections import deque

PATTERNS = {
    "0001011101110": "OPEN",
    "0001010111110": "CLOSE",
    "0001010111010": "LEFT",
    "0001011101010": "RIGHT",
    "0001010111011": "UP_GYRO",
    "0001011111011": "DOWN_GYRO",
    "0001011111010": "UP_STACK",
    "0001010101110": "DOWN_STACK",
    "0001011101011": "READY",
}
ALLOWED = {
    "gyromite": {"OPEN", "CLOSE", "LEFT", "RIGHT", "UP_GYRO", "DOWN_GYRO", "READY"},
    "stack_up": {"OPEN", "CLOSE", "LEFT", "RIGHT", "UP_STACK", "DOWN_STACK", "READY"},
}


class ExactFrameDecoder:
    """Decode the game's complete rendered frames without camera timing guesses."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.frames = deque(maxlen=13)
        self.last_index = None

    def feed(self, index, level, game):
        if game not in ALLOWED or level not in ("0", "1", "N") or not isinstance(index, int):
            self.reset()
            return None
        if self.last_index is not None and index != self.last_index + 1:
            self.frames.clear()
        self.last_index = index
        if level == "N":
            self.frames.clear()
            return None
        self.frames.append(level)
        if len(self.frames) != 13:
            return None
        bits = "".join(self.frames)
        command = PATTERNS.get(bits)
        if command not in ALLOWED[game]:
            return None
        self.frames.clear()
        return command, bits


class FrameTestDetector:
    """Recognize the games' sustained or alternating Test light frames."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.last_index = None
        self.last_level = None
        self.green_frames = 0
        self.alternating_edges = 0

    def feed(self, index, level):
        if level not in ("0", "1", "N") or not isinstance(index, int):
            self.reset()
            return False
        if self.last_index is not None and index != self.last_index + 1:
            self.reset()
        self.green_frames = self.green_frames + 1 if level == "1" else 0
        self.alternating_edges = (
            self.alternating_edges + 1
            if self.last_level is not None and (level == "1") != (self.last_level == "1") else 0
        )
        self.last_index = index
        self.last_level = level
        return self.green_frames >= 36 or self.alternating_edges >= 12
