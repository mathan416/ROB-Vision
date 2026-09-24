import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from controller.model import StackState, GyroState
from controller.optical import OpticalDecoder, PATTERNS
from controller.service import Controller


class OpticalTests(unittest.TestCase):
    def trace(self, pattern, game, fps=240):
        decoder = OpticalDecoder()
        found = []
        # A bright idle edge begins the transmission's dark preamble.
        bits = "1" + pattern + "0" * 8
        for sample in range(int(len(bits) * fps / 60)):
            t = sample / fps
            bit = bits[int(t * 60)]
            result = decoder.feed(t, .8 if bit == "1" else .04, game)
            if result:
                found.append(result.command)
        return found

    def test_all_rom_patterns_once(self):
        for pattern, command in PATTERNS.items():
            game = "stack_up" if command.endswith("STACK") else "gyromite"
            self.assertEqual(self.trace(pattern, game), [command], command)

    def test_wrong_game_and_partial_rejected(self):
        self.assertEqual(self.trace("0001011111010", "gyromite"), [])
        self.assertEqual(self.trace("0001011101", "stack_up"), [])

    def test_two_identical_transmissions_are_two_actions(self):
        decoder = OpticalDecoder()
        bits = "1" + "0001010101110" + "0" * 3 + "1" + "0001010101110" + "0" * 5
        found = []
        for sample in range(len(bits) * 4):
            t = sample / 240
            detected = decoder.feed(t, .8 if bits[int(t * 60)] == "1" else .04, "stack_up")
            if detected:
                found.append(detected.command)
        self.assertEqual(found, ["DOWN_STACK", "DOWN_STACK"])


class ModelTests(unittest.TestCase):
    def test_stack_group_carry_and_rejection(self):
        state = StackState()
        for _ in range(3):
            self.assertIsNone(state.apply("DOWN"))
        self.assertIsNone(state.apply("CLOSE"))
        self.assertEqual(state.held, ["blue", "white", "red"])
        self.assertEqual(sum(map(len, state.trays)) + len(state.held), 5)
        before = state.snapshot()
        self.assertIsNotNone(state.apply("DOWN"))
        self.assertEqual(state.snapshot(), before)

    def test_gyro_bounds_and_ready(self):
        model = GyroState()
        self.assertIsNotNone(model.apply("UP"))
        controller = Controller()
        controller.select("gyromite")
        self.assertEqual(controller.command("READY")["robot"]["station"], 2)

    def test_camera_trace_reaches_shared_stack_state(self):
        controller = Controller()
        controller.select("stack_up")
        bits = "1" + "0001010101110" + "0" * 5
        for sample in range(len(bits) * 4):
            t = sample / 240
            controller.sample(t, .8 if bits[int(t * 60)] == "1" else .04)
        snapshot = controller.snapshot()
        self.assertEqual(snapshot["robot"]["height"], 5)
        self.assertEqual([event["kind"] for event in snapshot["events"]], ["session", "decoded", "action"])


if __name__ == "__main__":
    unittest.main()
