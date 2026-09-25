"""Decode complete, ROM-derived R.O.B. light messages from timestamped samples.

Each sample is (monotonic_seconds, brightness). The light value can change every
roughly 60 Hz game frame. Higher capture rates give more timing margin; the
decoder uses run durations rather than assuming one camera frame per game frame.
"""

from collections import deque
from dataclasses import dataclass

FRAME_SECONDS = 1 / 60.0
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


@dataclass(frozen=True)
class Detection:
    command: str
    pattern: str
    start: float
    end: float


class OpticalDecoder:
    def __init__(self, threshold=0.38, frame_seconds=FRAME_SECONDS):
        self.threshold = threshold
        self.frame_seconds = frame_seconds
        self.runs = deque(maxlen=32)
        self.level = None
        self.run_start = None
        self.last_time = None
        self.last_emitted_end = -1.0

    def reset(self):
        self.runs.clear()
        self.level = self.run_start = self.last_time = None
        self.last_emitted_end = -1.0

    def feed(self, timestamp, brightness, game):
        """Return a detection only after the entire final bit has been observed."""
        if game not in ALLOWED or not 0 <= brightness <= 1:
            return None
        if self.last_time is not None and (timestamp <= self.last_time or timestamp - self.last_time > .5):
            self.reset()
        self.last_time = timestamp
        level = int(brightness >= self.threshold)
        if self.level is None:
            self.level, self.run_start = level, timestamp
            return None
        if level == self.level:
            if level == 0 and timestamp - self.run_start >= self.frame_seconds * .75:
                return self._candidate(game, timestamp)
            return None
        duration = timestamp - self.run_start
        self.runs.append((self.level, self.run_start, timestamp, duration))
        self.level, self.run_start = level, timestamp
        return None

    def _candidate(self, game, now):
        # Reconstruct bit cells from measured runs. An idle dark stretch may be
        # long, so examine suffixes that begin with a 3-frame dark preamble.
        runs = list(self.runs) + [(0, self.run_start, now, now - self.run_start)]
        for first in range(max(0, len(runs) - 20), len(runs)):
            if runs[first][0] != 0:
                continue
            bits = ""
            plausible = True
            for level, _start, _end, duration in runs[first:]:
                cells = round(duration / self.frame_seconds)
                error = abs(duration / self.frame_seconds - cells)
                if cells < 1 or cells > 8 or error > .42:
                    plausible = False
                    break
                bits += str(level) * cells
                if len(bits) >= 13:
                    break
            if not plausible or len(bits) != 13:
                continue
            command = PATTERNS.get(bits)
            if command not in ALLOWED[game]:
                continue
            start = runs[first][1]
            end = runs[-1][2]
            if end <= self.last_emitted_end or start < self.last_emitted_end:
                continue
            self.last_emitted_end = end
            return Detection(command, bits, start, end)
        return None
