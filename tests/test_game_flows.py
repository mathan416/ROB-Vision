"""Independent game-frame-to-virtual-object flows for each supported game."""

import unittest

from controller.optical import PATTERNS
from controller.service import Controller


BY_COMMAND = {command: pattern for pattern, command in PATTERNS.items()}


class FrameFlow:
    def __init__(self, game):
        self.controller = Controller()
        self.controller.select(game)
        self.frame = 100

    def send(self, command):
        before = self.controller.snapshot()['sequence']
        self.frame += 16
        self.controller.emulator_command(self.controller.game, BY_COMMAND[command], 123, self.frame)
        events = [event for event in self.controller.snapshot()['events'] if event['seq'] > before]
        assert [event['command'] for event in events if event['kind'] == 'decoded'] == [command], events
        return events

    def state(self):
        return self.controller.snapshot()['robot']


class GameFlowTests(unittest.TestCase):
    def test_gyromite_spinner_to_red_pad_and_release(self):
        game = FrameFlow('gyromite')
        for command in ['DOWN_GYRO', 'DOWN_GYRO', 'CLOSE', 'UP_GYRO', 'UP_GYRO',
                        'RIGHT', 'RIGHT', 'RIGHT', 'DOWN_GYRO', 'DOWN_GYRO', 'OPEN']:
            game.send(command)
        self.assertEqual(game.state()['pieces']['a'], 'spinner')
        self.assertTrue(game.state()['spinning']['a'])
        for command in ['CLOSE', 'UP_GYRO', 'UP_GYRO', 'LEFT', 'LEFT',
                        'DOWN_GYRO', 'DOWN_GYRO', 'OPEN']:
            game.send(command)
        self.assertEqual(game.state()['pieces']['a'], 'red_pad')
        self.assertEqual(game.state()['pads'], {'red': True, 'blue': False})
        game.send('CLOSE')
        game.send('UP_GYRO')
        self.assertEqual(game.state()['pads'], {'red': False, 'blue': False})
        self.assertEqual(game.state()['pieces']['b'], 'holder_b')

    def test_stack_up_red_then_grouped_blue_white_transfer(self):
        game = FrameFlow('stack_up')
        for command in ['DOWN_STACK', 'CLOSE', 'UP_STACK', 'RIGHT'] + ['DOWN_STACK'] * 5 + ['OPEN']:
            game.send(command)
        self.assertEqual(game.state()['trays'][3], ['red'])
        for command in ['UP_STACK', 'UP_STACK', 'LEFT', 'CLOSE', 'RIGHT', 'DOWN_STACK']:
            game.send(command)
        before = game.state()
        events = game.send('DOWN_STACK')
        self.assertTrue(any(event['kind'] == 'blocked' for event in events))
        self.assertEqual(game.state(), before)
        game.send('OPEN')
        self.assertEqual(game.state()['trays'][3], ['red', 'blue', 'white'])
        self.assertEqual(game.state()['trays'][2], ['green', 'yellow'])
        self.assertEqual(sum(map(len, game.state()['trays'])) + len(game.state()['held']), 5)

    def test_game_specific_vertical_commands_never_cross_modes(self):
        gyro = FrameFlow('gyromite')
        stack = FrameFlow('stack_up')
        gyro_before, stack_before = gyro.state(), stack.state()
        for command, game in [('DOWN_STACK', gyro), ('DOWN_GYRO', stack)]:
            with self.assertRaises(ValueError):
                game.controller.emulator_command(game.controller.game, BY_COMMAND[command], 123, 200)
        self.assertEqual(gyro.state(), gyro_before)
        self.assertEqual(stack.state(), stack_before)


if __name__ == '__main__':
    unittest.main()
