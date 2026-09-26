import unittest

from controller.model import GyroState, StackState
from controller.optical import ALLOWED, PATTERNS, ExactFrameDecoder, FrameTestDetector
from controller.service import Controller


class FrameTests(unittest.TestCase):
    def test_all_complete_patterns_match_only_their_game(self):
        for pattern, command in PATTERNS.items():
            game = 'stack_up' if command.endswith('STACK') else 'gyromite'
            for candidate in ('gyromite', 'stack_up'):
                decoder = ExactFrameDecoder()
                matches = [decoder.feed(index, level, candidate)
                           for index, level in enumerate('N' + pattern)]
                self.assertEqual(matches[-1], (command, pattern) if command in ALLOWED[candidate] else None)
                self.assertEqual(sum(match is not None for match in matches),
                                 int(command in ALLOWED[candidate]))

    def test_gap_and_non_light_frame_reject_partial_command(self):
        decoder = ExactFrameDecoder()
        self.assertTrue(all(decoder.feed(i, bit, 'stack_up') is None
                            for i, bit in enumerate('0001011')))
        self.assertTrue(all(decoder.feed(i + 8, bit, 'stack_up') is None
                            for i, bit in enumerate('111010')))
        decoder.reset()
        self.assertTrue(all(decoder.feed(i, bit, 'stack_up') is None
                            for i, bit in enumerate('0001011N111010')))

    def test_test_frames_are_distinct_from_commands(self):
        for pattern in PATTERNS:
            detector = FrameTestDetector()
            self.assertFalse(any(detector.feed(i, bit) for i, bit in enumerate(pattern)), pattern)
        detector = FrameTestDetector()
        detector.reset()
        self.assertTrue(any(detector.feed(i, '1') for i in range(36)))
        detector.reset()
        self.assertTrue(any(detector.feed(i, str(i % 2)) for i in range(14)))
        detector.reset()
        self.assertTrue(any(detector.feed(i, '1' if i % 2 else 'N') for i in range(14)))
        detector.reset()
        self.assertFalse(any(detector.feed(i, str(i % 2)) for i in range(6)))
        self.assertFalse(detector.feed(20, '1'))

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

    def test_frame_test_signal_lights_robot_without_moving_it(self):
        controller = Controller()
        controller.select('gyromite')
        initial = controller.snapshot()['robot']
        self.assertFalse(controller.snapshot()['test']['flash_active'])
        controller.receiver_seen('RetroPie', 'gyromite', 'gyromite')
        controller.receiver_seen('RetroPie', 'gyromite', 'gyromite')
        state = controller.snapshot()
        self.assertTrue(state['test']['flash_active'])
        self.assertFalse(state['test']['ready'])
        self.assertEqual(state['robot'], initial)
        self.assertEqual(sum(event['message'].startswith('Game-frame Test signal detected')
                             for event in state['events']), 1)
        controller.emulator_command('gyromite', '0001011101011', 123, 420)
        self.assertTrue(controller.snapshot()['test']['ready'])
        controller.test_ready_at -= 1.1
        self.assertFalse(controller.snapshot()['test']['ready'])
        controller.emulator_command('gyromite', '0001011101011', 123, 421)
        self.assertTrue(controller.snapshot()['test']['ready'])
        controller.emulator_command('gyromite', '0001011111011', 123, 440)
        self.assertFalse(controller.snapshot()['test']['ready'])
        self.assertFalse(controller.snapshot()['test']['flash_active'])

    def test_test_light_stops_when_signal_expires_and_ignores_wrong_game(self):
        controller = Controller()
        controller.select('stack_up')
        controller.receiver_seen('RetroPie', 'stack_up', 'gyromite')
        self.assertFalse(controller.snapshot()['test']['flash_active'])
        controller.receiver_seen('RetroPie', 'stack_up', 'stack_up')
        self.assertTrue(controller.snapshot()['test']['flash_active'])
        controller.test_flash_seen_at -= 1
        self.assertFalse(controller.snapshot()['test']['flash_active'])

    def test_active_console_rejects_other_console_frames(self):
        controller = Controller()
        controller.select('stack_up')
        controller.active_receiver = 'batocera'
        controller.receiver_seen('Batocera', 'stack_up')
        controller.receiver_seen('RetroPie', 'stack_up')
        self.assertEqual(controller.snapshot()['link']['receiver'], 'Batocera')
        with self.assertRaisesRegex(ValueError, 'another console'):
            controller.emulator_command('stack_up', '0001011101010', 123, 400, 'retropie')
        self.assertEqual(controller.stack.station, 3)
        controller.emulator_command('stack_up', '0001011101010', 123, 400, 'batocera')
        self.assertEqual(controller.stack.station, 4)


class ModelTests(unittest.TestCase):
    def test_stack_group_carry_and_rejection(self):
        state = StackState()
        for _ in range(3):
            self.assertIsNone(state.apply('DOWN'))
        self.assertIsNone(state.apply('CLOSE'))
        self.assertEqual(state.held, ['blue', 'white', 'red'])
        self.assertEqual(sum(map(len, state.trays)) + len(state.held), 5)
        before = state.snapshot()
        self.assertIsNotNone(state.apply('DOWN'))
        self.assertEqual(state.snapshot(), before)

    def test_gyro_bounds_and_ready(self):
        model = GyroState()
        self.assertIsNotNone(model.apply('UP'))
        controller = Controller()
        controller.select('gyromite')
        self.assertEqual(controller.command('READY')['robot']['station'], 2)

    def test_setup_ready_signal_and_receiver_status(self):
        controller = Controller()
        controller.select('stack_up')
        self.assertFalse(controller.command('READY', 'manual')['test']['ready'])
        controller.emulator_command('stack_up', '0001011101011', 123, 401)
        self.assertTrue(controller.snapshot()['test']['ready'])
        controller.receiver_seen('RetroPie')
        self.assertTrue(controller.snapshot()['link']['online'])
        self.assertFalse(controller.select('gyromite')['test']['ready'])

    def test_held_unspun_gyro_press_releases_on_lift(self):
        model = GyroState()
        for command in ('DOWN', 'DOWN', 'CLOSE', 'UP', 'RIGHT'):
            model.apply(command)
        self.assertEqual(model.snapshot()['pads'], {'red': False, 'blue': False})
        model.apply('DOWN')
        self.assertEqual(model.snapshot()['pads'], {'red': True, 'blue': False})
        model.apply('UP')
        self.assertEqual(model.snapshot()['pads'], {'red': False, 'blue': False})

    def test_gate_assist_is_immediate_and_expires(self):
        controller = Controller()
        controller.select('gyromite')
        blue = controller.gate_assist('blue', True)
        self.assertEqual(blue['robot']['pads'], {'red': False, 'blue': True})
        red = controller.gate_assist('red', True)
        self.assertEqual(red['robot']['pads'], {'red': True, 'blue': True})
        controller.gate_assist('blue', False)
        controller.gyro.assisted_until['red'] = 0.01
        expired = controller.snapshot()
        self.assertEqual(expired['robot']['pads'], {'red': False, 'blue': False})
        self.assertEqual(expired['robot']['pieces'], {'a': 'holder_a', 'b': 'holder_b'})

    def test_gate_assist_rejects_other_game(self):
        controller = Controller()
        controller.select('stack_up')
        with self.assertRaises(ValueError):
            controller.gate_assist('red', True)


if __name__ == '__main__':
    unittest.main()
