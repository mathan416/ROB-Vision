import sys
import time
import types
import unittest
import random
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from controller.model import StackState, GyroState
from controller.optical import ExactFrameDecoder, OpticalDecoder, PATTERNS, TestFlashDetector
from controller.service import Controller, preferred_kiyo_capture_mode
from python.main import preferred_camera_roi


class OpticalTests(unittest.TestCase):
    def test_emulator_command_checks_game_pattern_and_retries_once(self):
        controller = Controller()
        controller.select('stack_up')
        controller.emulator_command('stack_up', '0001011101010', 123, 400)
        self.assertEqual(controller.stack.station, 4)
        controller.emulator_command('stack_up', '0001011101010', 123, 400)
        self.assertEqual(controller.stack.station, 4)
        self.assertTrue(controller.snapshot()['input']['frame_hook'])
        with self.assertRaises(ValueError):
            controller.emulator_command('stack_up', '0001011111011', 123, 401)
        with self.assertRaises(ValueError):
            controller.emulator_command('gyromite', '0001011101010', 123, 402)

    def test_exact_frame_decoder_matches_only_complete_game_patterns(self):
        decoder = ExactFrameDecoder()
        seen = [decoder.feed(i, bit, 'stack_up') for i, bit in enumerate('N' + '0001011111010')]
        self.assertEqual(seen[-1], ('UP_STACK', '0001011111010'))
        self.assertEqual(sum(result is not None for result in seen), 1)
        decoder.reset()
        wrong_game = [decoder.feed(i, bit, 'stack_up') for i, bit in enumerate('0001011111011')]
        self.assertTrue(all(result is None for result in wrong_game))
        decoder.reset()
        interrupted = [decoder.feed(i, bit, 'stack_up') for i, bit in enumerate('0001011')]
        interrupted += [decoder.feed(i + 8, bit, 'stack_up') for i, bit in enumerate('111010')]
        self.assertTrue(all(result is None for result in interrupted))

    def test_kiyo_capture_mode_is_allowlisted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data').mkdir()
            with patch('controller.service.ROOT', root):
                self.assertEqual(preferred_kiyo_capture_mode(), 'mjpg480')
                (root / 'data' / 'camera-mode').write_text('yuyv720\n')
                self.assertEqual(preferred_kiyo_capture_mode(), 'yuyv720')
                (root / 'data' / 'camera-mode').write_text('unsupported\n')
                self.assertEqual(preferred_kiyo_capture_mode(), 'mjpg480')

    def test_saved_camera_sampling_box(self):
        with patch.dict('os.environ', {'ROB_VISION_CAMERA_ROI': '0.4,0.30,0.055,0.06'}):
            self.assertEqual(preferred_camera_roi(), [0.4, 0.30, 0.055, 0.06])
        with patch.dict('os.environ', {'ROB_VISION_CAMERA_ROI': '0.99,0.30,0.055,0.06'}):
            self.assertIsNone(preferred_camera_roi())
        with patch.dict('os.environ', {'ROB_VISION_CAMERA_ROI': 'nan,0.30,0.055,0.06'}):
            self.assertIsNone(preferred_camera_roi())
        with self.assertRaises(ValueError):
            Controller().start_camera(roi=[float('nan'), 0.3, 0.055, 0.06])

    def test_sustained_test_flashes_are_distinct_from_commands(self):
        for fps in (60, 120):
            detector = TestFlashDetector()
            observed = False
            for sample in range(fps):
                frame = int(((sample + .5) / fps) * 60)
                observed |= detector.feed((sample + .5) / fps, .8 if frame % 2 else .04)
            self.assertTrue(observed, fps)
        detector.reset()
        self.assertTrue(any(detector.feed(i / 60, .8) for i in range(60)))
        detector.reset()
        bits = '1' + next(iter(PATTERNS)) + '0000'
        self.assertFalse(any(detector.feed(i / 60, .8 if bit == '1' else .04) for i, bit in enumerate(bits)))

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

    def test_idealized_60_fps_can_decode_each_pattern(self):
        for pattern, command in PATTERNS.items():
            game = "stack_up" if command.endswith("STACK") else "gyromite"
            self.assertEqual(self.trace(pattern, game, fps=60), [command], command)

    def test_first_command_after_long_idle_uses_three_dark_preamble_frames(self):
        # The live Stack-Up RIGHT trace began after 19 seconds of darkness.
        # Camera samples preserved the 13 bit cells, but the first dark run
        # must be trimmed to the message's three-frame preamble.
        decoder = OpticalDecoder()
        samples = [(-.0661, 0), (-.0569, 0), (-.0487, 0),
                   (-.0293, 0), (-.0167, 0), (0, 1), (.0215, 0),
                   (.0379, 1), (.0542, 1), (.0702, 1), (.0892, 0),
                   (.1035, 1), (.1200, 0), (.1392, 1), (.1533, 0),
                   (.1702, 0), (.1845, 0)]
        observed = []
        for frame in range(60 * 19):
            self.assertIsNone(decoder.feed(frame / 60, .02, "stack_up"))
        start = 19.5
        for offset, level in samples:
            detection = decoder.feed(start + offset, .4 if level else .02, "stack_up")
            if detection:
                observed.append(detection.command)
        self.assertEqual(observed, ["RIGHT"])

    def test_live_60_fps_jittered_dark_cell_still_requires_unique_pattern(self):
        decoder = OpticalDecoder()
        for frame in range(60 * 3):
            decoder.feed(frame / 60, .02, "stack_up")
        start = 3.2
        samples = [(-.064, 0), (-.046, 0), (-.031, 0), (-.015, 0),
                   (0, 1), (.016, 0), (.034, 1), (.054, 1), (.072, 1),
                   (.085, 0), (.105, 1), (.127, 0), (.136, 1),
                   (.153, 0), (.162, 0), (.170, 0), (.185, 0)]
        observed = []
        for offset, level in samples:
            detection = decoder.feed(start + offset, .4 if level else .02, "stack_up")
            if detection:
                observed.append(detection.command)
        self.assertEqual(observed, ["RIGHT"])

    def test_realistic_camera_rates_fail_closed_when_bits_are_missed(self):
        # Unsynchronized 30/60 fps capture of 60 Hz one-frame bits cannot be
        # assumed complete. Preserve correct-command rate and no wrong actions.
        for fps in (30, 60):
            rng = random.Random(416)
            correct = wrong = 0
            for pattern, command in PATTERNS.items():
                game = "stack_up" if command.endswith("STACK") else "gyromite"
                for _ in range(100):
                    phase = rng.random()
                    bits = "1" + pattern + "00000"
                    decoder = OpticalDecoder()
                    found = []
                    for sample in range(int(len(bits) * fps / 60) + 5):
                        timestamp = (sample + phase) / fps + rng.uniform(-.0007, .0007)
                        bit = bits[min(int(timestamp * 60), len(bits) - 1)]
                        brightness = (.85 if bit == "1" else .05) + rng.uniform(-.025, .025)
                        detection = decoder.feed(timestamp, brightness, game)
                        if detection:
                            found.append(detection.command)
                    correct += found == [command]
                    wrong += bool(found and found != [command])
            self.assertEqual(wrong, 0, fps)
            if fps == 30:
                self.assertEqual(correct, 0)
            else:
                self.assertGreaterEqual(correct, 640)

    def test_idle_and_test_flashes_do_not_move_robot_at_60_fps(self):
        rng = random.Random(416)
        for game in ("gyromite", "stack_up"):
            for alternating in (False, True):
                decoder = OpticalDecoder()
                for sample in range(1800):
                    brightness = (.85 if sample % 2 else .05) if alternating else .05 + rng.uniform(-.025, .025)
                    self.assertIsNone(decoder.feed((sample + .5) / 60, brightness, game))

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
    def test_test_flashes_light_robot_without_moving_it(self):
        controller = Controller()
        controller.select('gyromite')
        controller.camera['state'] = 'capturing'
        controller.arm_test()
        initial = controller.snapshot()['robot']
        for sample in range(30):
            controller.sample((sample + .5) / 60, .8 if sample % 2 else .04)
        snapshot = controller.snapshot()
        self.assertTrue(snapshot['test']['flash_active'])
        self.assertFalse(snapshot['test']['ready'])
        self.assertEqual(snapshot['robot'], initial)
        controller.command('READY', 'camera')
        self.assertTrue(controller.snapshot()['test']['ready'])
        controller.command('DOWN_GYRO', 'camera')
        self.assertFalse(controller.snapshot()['test']['armed'])

    def test_steady_green_test_signal_announced_once(self):
        controller = Controller()
        controller.select('gyromite')
        controller.camera['state'] = 'capturing'
        controller.arm_test()
        initial = controller.snapshot()['robot']
        for sample in range(180):
            controller.sample(sample / 60, .25)
        snapshot = controller.snapshot()
        self.assertTrue(snapshot['test']['flash_active'])
        self.assertEqual(snapshot['robot'], initial)
        self.assertEqual(sum(event['message'].startswith('Test-mode optical signal detected')
                             for event in snapshot['events']), 1)

    def test_stack_up_alternating_test_signal_does_not_move_blocks(self):
        controller = Controller()
        controller.select('stack_up')
        controller.camera['state'] = 'capturing'
        controller.arm_test()
        initial = controller.snapshot()['robot']
        for sample in range(120):
            controller.sample((sample + .5) / 60, .59 if sample % 2 else .01)
        snapshot = controller.snapshot()
        self.assertTrue(snapshot['test']['flash_active'])
        self.assertEqual(snapshot['robot'], initial)
        self.assertEqual(sum(event['message'].startswith('Test-mode optical signal detected')
                             for event in snapshot['events']), 1)

    def test_camera_reconnect_reopens_after_capture_failure(self):
        captures = []
        requested_rates = []

        class FailedCapture:
            def __init__(self, _index):
                self.released = False
                captures.append(self)

            def isOpened(self):
                return True

            def set(self, _property, _value):
                requested_rates.append(_value)

            def read(self):
                return False, None

            def release(self):
                self.released = True

        fake_cv2 = types.SimpleNamespace(VideoCapture=FailedCapture, CAP_PROP_FPS=5)
        with patch.dict(sys.modules, {"cv2": fake_cv2}), patch("controller.service.capture_devices", return_value=[{"path": "/dev/video9", "name": "Test camera"}]):
            controller = Controller()
            controller.start_camera()
            controller.capture_thread.join(timeout=1)
            self.assertEqual(controller.snapshot()["camera"]["state"], "fault")
            controller.reconnect_camera()
            controller.capture_thread.join(timeout=1)
            self.assertEqual(len(captures), 2)
            self.assertEqual(requested_rates, [60, 60])
            self.assertTrue(all(capture.released for capture in captures))
            self.assertEqual(controller.snapshot()["camera"]["state"], "fault")

    def test_camera_stop_resets_stale_fault_readings(self):
        with patch("controller.service.capture_devices", return_value=[]):
            controller = Controller()
            controller.camera.update(state="fault", fps=90, brightness=.7, last_frame=time.time())
            camera = controller.stop_camera()["camera"]
            self.assertEqual(camera["state"], "offline")
            self.assertEqual((camera["fps"], camera["brightness"], camera["last_frame"]), (0, 0, None))

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

    def test_setup_ready_signal_and_receiver_status(self):
        controller = Controller()
        controller.select("stack_up")
        self.assertFalse(controller.arm_test()["test"]["ready"])
        self.assertFalse(controller.command("READY", "manual")["test"]["ready"])
        self.assertTrue(controller.command("READY", "camera")["test"]["ready"])
        controller.receiver_seen("RetroPie")
        self.assertTrue(controller.snapshot()["link"]["online"])
        self.assertFalse(controller.select("gyromite")["test"]["armed"])

    def test_held_unspun_gyro_press_releases_on_lift(self):
        model = GyroState()
        model.apply("DOWN")
        model.apply("DOWN")
        model.apply("CLOSE")
        model.apply("UP")
        model.apply("RIGHT")
        self.assertEqual(model.snapshot()["pads"], {"red": False, "blue": False})
        model.apply("DOWN")
        self.assertEqual(model.snapshot()["pads"], {"red": True, "blue": False})
        model.apply("UP")
        self.assertEqual(model.snapshot()["pads"], {"red": False, "blue": False})

    def test_gate_assist_is_immediate_and_expires(self):
        controller = Controller()
        controller.select("gyromite")
        blue = controller.gate_assist("blue", True)
        self.assertEqual(blue["robot"]["pads"], {"red": False, "blue": True})
        self.assertEqual(blue["robot"]["pieces"]["b"], "blue_pad")
        red = controller.gate_assist("red", True)
        self.assertEqual(red["robot"]["pads"], {"red": True, "blue": True})
        controller.gate_assist("blue", False)
        self.assertEqual(controller.snapshot()["robot"]["pads"], {"red": True, "blue": False})
        controller.gyro.assisted_until["red"] = 0.01
        expired = controller.snapshot()
        self.assertEqual(expired["robot"]["pads"], {"red": False, "blue": False})
        self.assertEqual(expired["robot"]["pieces"], {"a": "holder_a", "b": "holder_b"})
        self.assertIn("timed out", expired["events"][-1]["message"])

    def test_gate_assist_rejects_other_game_and_camera_capture(self):
        controller = Controller()
        controller.select("stack_up")
        with self.assertRaises(ValueError):
            controller.gate_assist("red", True)
        controller.select("gyromite")
        controller.camera["state"] = "capturing"
        with self.assertRaises(ValueError):
            controller.gate_assist("red", True)

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
