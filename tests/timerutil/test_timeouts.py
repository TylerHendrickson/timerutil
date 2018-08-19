import signal
import time
import unittest

from timerutil import timeouts

from tests.compat import mock


class TimeoutManagerInitTestCase(unittest.TestCase):
    def test_init_with_default_args(self):
        manager = timeouts.TimeoutManager(seconds=1)

        self.assertEqual(manager.seconds, 1)
        self.assertEqual(manager.timeout_message, timeouts.DEFAULT_TIMEOUT_MESSAGE)
        self.assertFalse(manager.suppress_errors)
        self.assertIsNone(manager._original_alarm_handler)

    def test_init_with_explicit_args(self):
        manager = timeouts.TimeoutManager(seconds=1, timeout_message='A Message', suppress_timeout_errors=True)

        self.assertEqual(manager.seconds, 1)
        self.assertEqual(manager.timeout_message, 'A Message')
        self.assertTrue(manager.suppress_errors)
        self.assertIsNone(manager._original_alarm_handler)


class TimeoutManagerReprTestCase(unittest.TestCase):
    def test_repr_result(self):
        self.assertEqual(
            repr(timeouts.TimeoutManager(10)),
            '<{}: {} seconds>'.format(timeouts.TimeoutManager.__name__, 10)
        )


class TimeoutManagerTimeoutHandlerTestCase(unittest.TestCase):
    def test_raises_TimeoutError(self):
        manager = timeouts.TimeoutManager(1)

        with self.assertRaises(timeouts.TimeoutError) as ctx:
            manager._timeout_handler(None, None)

        self.assertEqual(str(ctx.exception), manager.timeout_message)


class TimeoutManagerEnterTestCase(unittest.TestCase):
    def test_alarm_handler_is_replaced(self):
        original_handler = signal.getsignal(signal.SIGALRM)

        with timeouts.TimeoutManager(10) as manager:
            self.assertIs(original_handler, manager._original_alarm_handler)
            self.assertEqual(signal.getsignal(signal.SIGALRM), manager._timeout_handler)

    def test_arranges_alarm_arrival(self):
        with mock.patch('signal.alarm') as mock_alarm:
            with timeouts.TimeoutManager(10) as manager:
                mock_alarm.assert_called_once_with(manager.seconds)


class TimeoutManagerExitTestCase(unittest.TestCase):
    def test_alarm_handler_is_restored(self):
        original_handler = signal.getsignal(signal.SIGALRM)

        with timeouts.TimeoutManager(10) as manager:
            pass

        self.assertIs(original_handler, signal.getsignal(signal.SIGALRM))

    def test_raises_TimeoutError_when_suppress_errors_is_False(self):
        with self.assertRaises(timeouts.TimeoutError) as ctx:
            with timeouts.TimeoutManager(1, suppress_timeout_errors=False) as manager:
                time.sleep(1.1)

        self.assertEqual(str(ctx.exception), manager.timeout_message)

    def test_does_not_raise_TimeoutError_when_suppress_errors_is_True(self):
        try:
            with timeouts.TimeoutManager(1, suppress_timeout_errors=True):
                time.sleep(1.1)
        except timeouts.TimeoutError:
            self.fail('TimeoutError unexpectedly raised')

    def test_suppresses_only_TimeoutError_exceptions_when_suppress_errors_is_True(self):
        with self.assertRaises(ValueError) as ctx:
            with timeouts.TimeoutManager(1, suppress_timeout_errors=True):
                raise ValueError('Not a TimeoutError')
