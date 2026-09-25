import unittest
from unittest.mock import patch

from controller.matrix import MatrixDisplay, MatrixMode


def snapshot(game=None, sequence=0, command=None, kind='action', test=None):
    return {'game': game, 'sequence': sequence,
            'test': test or {'ready': False, 'flash_active': False},
            'events': [{'kind': kind, 'command': command}] if command else []}


class MatrixTests(unittest.TestCase):
    def test_game_states_and_only_accepted_actions_animate(self):
        sent = []
        display = MatrixDisplay(call=lambda *args: sent.append(args))
        display.update(snapshot())
        self.assertTrue(display.status()['bridge_ok'])
        self.assertEqual(display.status()['mode'], 'idle')
        display.update(snapshot('gyromite', 1, 'LEFT_GYRO'))
        display.update(snapshot('stack_up', 2, 'OPEN'))
        display.update(snapshot('stack_up', 3, 'RIGHT', kind='decoded'))
        self.assertEqual(sent, [('set_rob_display', 1, 0), ('set_rob_display', 2, 1),
                                ('set_rob_display', 3, 5)])

    def test_test_and_pairing_priority(self):
        sent = []
        display = MatrixDisplay(call=lambda *args: sent.append(args))
        display.update(snapshot('gyromite', test={'ready': True, 'flash_active': False}))
        display.update(snapshot('gyromite', test={'ready': True, 'flash_active': True}))
        display.show_pairing()
        display.update(snapshot('gyromite', test={'ready': True, 'flash_active': True}))
        self.assertEqual([call[1] for call in sent],
                         [MatrixMode.TEST, MatrixMode.TEST_FLASH, MatrixMode.PAIRING])
        display.clear_pairing()
        display.update(snapshot('gyromite'))
        self.assertEqual(sent[-1][1], MatrixMode.GYROMITE)

    def test_heartbeat_and_unavailable_bridge(self):
        sent = []
        display = MatrixDisplay(call=lambda *args: sent.append(args))
        display.update(snapshot())
        display.update(snapshot())
        self.assertEqual(len(sent), 1)
        with patch('controller.matrix.monotonic', return_value=display.last_sent + 1.1):
            display.update(snapshot())
        self.assertEqual(len(sent), 2)
        with patch('controller.matrix.monotonic', return_value=display.last_sent + 1.1):
            unavailable = MatrixDisplay(call=lambda *_args: (_ for _ in ()).throw(RuntimeError('bridge down')))
            self.assertFalse(unavailable.update(snapshot()))
            self.assertEqual(unavailable.last_error, 'bridge down')


if __name__ == '__main__':
    unittest.main()
