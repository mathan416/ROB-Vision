"""Authoritative virtual accessory state. No physical motors or switches."""

from dataclasses import dataclass, field
from time import monotonic

COLORS = ("green", "yellow", "blue", "white", "red")
COMMANDS = {"LEFT", "RIGHT", "UP", "DOWN", "OPEN", "CLOSE"}


@dataclass
class StackState:
    trays: list = field(default_factory=lambda: [[], [], list(COLORS), [], []])
    held: list = field(default_factory=list)
    station: int = 3
    height: int = 6
    grip: str = "open"

    def snapshot(self):
        return {"trays": [list(t) for t in self.trays], "held": list(self.held),
                "station": self.station, "height": self.height, "grip": self.grip}

    def apply(self, command):
        if command not in COMMANDS:
            return "Unknown Stack-Up command."
        trays = [list(t) for t in self.trays]
        held = list(self.held)
        station, height, grip = self.station, self.height, self.grip
        tray = trays[station - 1]
        if command == "UP":
            if height == 6:
                return "Arms are already at the highest level."
            height += 1
        elif command == "DOWN":
            if height == 1:
                return "Arms are already at the lowest level."
            if held and height - 1 <= len(tray):
                return "The carried blocks would collide with this tray stack."
            height -= 1
        elif command in ("LEFT", "RIGHT"):
            target = station + (-1 if command == "LEFT" else 1)
            if not 1 <= target <= 5:
                return "There is no tray in that direction."
            if held and height <= len(trays[target - 1]):
                return "Raise the carried blocks to clear the next tray."
            station = target
        elif command == "CLOSE":
            if grip == "closed":
                return "Hands are already closed."
            grip = "closed"
            if height <= len(tray):
                held = tray[height - 1:]
                del tray[height - 1:]
        elif command == "OPEN":
            if grip == "open":
                return "Hands are already open."
            if held:
                if height != len(tray) + 1:
                    return "Lower the carried blocks to the next free level before releasing."
                if len(tray) + len(held) > 5:
                    return "That tray cannot hold more than five blocks."
                tray.extend(held)
                held = []
            grip = "open"
        pieces = [*held, *(c for t in trays for c in t)]
        if sorted(pieces) != sorted(COLORS):
            return "Command would lose or duplicate a block."
        self.trays, self.held, self.station, self.height, self.grip = trays, held, station, height, grip
        return None


GYRO_STATIONS = ("holder_b", "holder_a", "red_pad", "blue_pad", "spinner")


@dataclass
class GyroState:
    station: int = 2
    height: int = 6
    grip: str = "open"
    held: str | None = None
    pieces: dict = field(default_factory=lambda: {"a": "holder_a", "b": "holder_b"})
    spinning_until: dict = field(default_factory=lambda: {"a": 0.0, "b": 0.0})
    assisted_until: dict = field(default_factory=lambda: {"red": 0.0, "blue": 0.0})
    spin_seconds: float = 55.0

    def expire_assist(self):
        expired = []
        now = monotonic()
        for color, which in (("red", "a"), ("blue", "b")):
            if self.assisted_until[color] and self.assisted_until[color] <= now:
                self.assisted_until[color] = 0.0
                self.spinning_until[which] = 0.0
                self.pieces[which] = f"holder_{which}"
                expired.append(color)
        return expired

    def assist_gate(self, color, pressed):
        if color not in ("red", "blue") or not isinstance(pressed, bool):
            raise ValueError("Choose a red or blue gate and a pressed state.")
        self.expire_assist()
        which = "a" if color == "red" else "b"
        if pressed:
            if self.held or self.pieces[which] != f"holder_{which}":
                raise ValueError("Return the gyro to its holder before using Gate Assist.")
            if f"{color}_pad" in self.pieces.values():
                raise ValueError("That pad already holds a gyro.")
            self.pieces[which] = f"{color}_pad"
            self.assisted_until[color] = monotonic() + 60.0
            self.spinning_until[which] = self.assisted_until[color]
            self.station = 3 if color == "red" else 4
            self.height = 2
            self.grip = "open"
        elif self.assisted_until[color]:
            self.assisted_until[color] = 0.0
            self.spinning_until[which] = 0.0
            self.pieces[which] = f"holder_{which}"

    def snapshot(self):
        now = monotonic()
        spinning = {key: self.spinning_until[key] > now for key in ("a", "b")}
        pads = {"red": False, "blue": False}
        for key, place in self.pieces.items():
            for color in pads:
                if place == f"{color}_pad" and spinning[key]:
                    pads[color] = True
        if self.held and self.height <= 2:
            station = GYRO_STATIONS[self.station - 1]
            for color in pads:
                if station == f"{color}_pad":
                    pads[color] = True
        return {"station": self.station, "height": self.height, "grip": self.grip,
                "held": self.held, "pieces": dict(self.pieces), "spinning": spinning, "pads": pads,
                "assist": {color: self.assisted_until[color] > now for color in pads}}

    def apply(self, command):
        if command not in COMMANDS:
            return "Unknown Gyromite command."
        if command in ("UP", "DOWN"):
            target = self.height + (2 if command == "UP" else -2)
            if not 1 <= target <= 6:
                return "Arm movement exceeds the six levels."
            self.height = target
        elif command in ("LEFT", "RIGHT"):
            target = self.station + (-1 if command == "LEFT" else 1)
            if not 1 <= target <= len(GYRO_STATIONS):
                return "There is no station in that direction."
            if self.held and self.height <= 2:
                return "Raise the gyro before turning."
            self.station = target
        elif command == "CLOSE":
            if self.grip == "closed":
                return "Hands are already closed."
            place = GYRO_STATIONS[self.station - 1]
            if self.height <= 2:
                candidates = [key for key, location in self.pieces.items() if location == place]
                if candidates:
                    self.held = candidates[0]
                    self.pieces[self.held] = "held"
            self.grip = "closed"
        elif command == "OPEN":
            if self.grip == "open":
                return "Hands are already open."
            if self.held:
                if self.height > 2:
                    return "Lower the gyro before releasing."
                place = GYRO_STATIONS[self.station - 1]
                if place in self.pieces.values():
                    return "That station already holds a gyro."
                self.pieces[self.held] = place
                if place == "spinner":
                    self.spinning_until[self.held] = monotonic() + self.spin_seconds
                self.held = None
            self.grip = "open"
        return None
