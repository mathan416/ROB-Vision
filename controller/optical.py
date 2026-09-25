"""Decode complete, ROM-derived R.O.B. light messages from timestamped samples.

Each sample is (monotonic_seconds, brightness). The light value can change every
roughly 60 Hz game frame. Higher capture rates give more timing margin; the
decoder uses run durations rather than assuming one camera frame per game frame.
"""

from collections import deque
from dataclasses import dataclass
from math import floor

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


class TestFlashDetector:
    """Recognize a sustained green Test field or frame-by-frame alternation."""

    def __init__(self, threshold=0.10):
        self.threshold = threshold
        self.reset()

    def reset(self):
        self.level = None
        self.last_time = None
        self.edges = deque(maxlen=13)
        self.green_since = None

    def feed(self, timestamp, brightness):
        if not 0 <= brightness <= 1:
            return False
        if self.last_time is not None and (timestamp <= self.last_time or timestamp - self.last_time > .1):
            self.reset()
        self.last_time = timestamp
        level = brightness >= self.threshold
        if level:
            if self.green_since is None:
                self.green_since = timestamp
        else:
            self.green_since = None
        sustained = self.green_since is not None and timestamp - self.green_since >= .6
        if self.level is None:
            self.level = level
            return False
        if level == self.level:
            return sustained
        self.level = level
        self.edges.append(timestamp)
        alternating = len(self.edges) == 13 and all(
            .009 <= b - a <= .027 for a, b in zip(self.edges, list(self.edges)[1:]))
        return sustained or alternating


class OpticalDecoder:
    def __init__(self, threshold=0.10, frame_seconds=FRAME_SECONDS):
        self.threshold = threshold
        self.frame_seconds = frame_seconds
        self.runs = deque(maxlen=32)
        self.samples = deque(maxlen=96)
        self.level = None
        self.run_start = None
        self.last_time = None
        self.last_emitted_end = -1.0

    def reset(self):
        self.runs.clear()
        self.samples.clear()
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
        self.samples.append((timestamp, level))
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
            candidate_runs = runs[first:]
            if runs[first][3] > self.frame_seconds * 8 and first + 1 < len(runs):
                # The first command after a long idle has no preceding flash.
                # Only its final three dark frames are the message preamble.
                bright_start = runs[first][2]
                candidate_runs = [(0, bright_start - 3 * self.frame_seconds,
                                   bright_start, 3 * self.frame_seconds)] + runs[first + 1:]
            bits = ""
            plausible = True
            for level, _start, _end, duration in candidate_runs:
                cells = round(duration / self.frame_seconds)
                error = abs(duration / self.frame_seconds - cells)
                if cells < 1 or cells > 8 or error > .50:
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
            start = candidate_runs[0][1]
            end = runs[-1][2]
            if end <= self.last_emitted_end or start < self.last_emitted_end:
                continue
            if self._possible_commands(game, start) != {command}:
                continue
            self.last_emitted_end = end
            return Detection(command, bits, start, end)
        return None

    def _possible_commands(self, game, observed_start):
        """Reject a run fit if sampled frames also admit another command."""
        samples = list(self.samples)
        first_bright = next((stamp for stamp, level in samples
                             if stamp >= observed_start and level == 1), None)
        if first_bright is None:
            return set()
        possible = set()
        # The first bright sample belongs to cell 3. Its exact position within
        # that cell is unknown, so test every phase allowed by the timestamps.
        lower = first_bright - 4 * self.frame_seconds
        upper = first_bright - 3 * self.frame_seconds
        boundaries = {lower, upper}
        for stamp, _level in samples:
            for cell in range(14):
                boundary = stamp - cell * self.frame_seconds
                if lower < boundary < upper:
                    boundaries.add(boundary)
        ordered = sorted(boundaries)
        for lower, upper in zip(ordered, ordered[1:]):
            start = (lower + upper) / 2
            levels = {}
            conflict = False
            for stamp, level in samples:
                cell = floor((stamp - start) / self.frame_seconds)
                if 0 <= cell < 13:
                    if cell in levels and levels[cell] != level:
                        conflict = True
                        break
                    levels[cell] = level
            if conflict or len(levels) < 10:
                continue
            for pattern, command in PATTERNS.items():
                if command in ALLOWED[game] and all(int(pattern[cell]) == level
                                                    for cell, level in levels.items()):
                    possible.add(command)
        return possible
