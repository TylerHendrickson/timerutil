import time
import unittest

from timerutil import waits

try:
    from unittest import mock
except ImportError:
    import mock


class WaiterEnterTestCase(unittest.TestCase):
    def test_records_start_time(self):
        waiter = waits.Waiter(0)

        with waiter:
            self.assertIsInstance(waiter._start_time, float)

    def test_context_manager_is_self(self):
        waiter = waits.Waiter(0)

        with waiter as waiter_ctx:
            pass

        self.assertIs(waiter, waiter_ctx)


class WaiterExitTestCase(unittest.TestCase):
    def _get_seconds_argument_for_mocked_sleep_call(self, mock_sleep_call):
        # Unpack the mock call into args, kwargs
        sleep_args, sleep_kwargs = mock_sleep_call

        # We expect `time.sleep` to be called with one positional argument or a `seconds` keyword argument
        if len(sleep_args) == 1:
            sleep_seconds = sleep_args[0]
        elif 'seconds' in sleep_kwargs:
            sleep_seconds = sleep_kwargs['seconds']
        else:
            self.fail(
                'Expected a mocked call to `time.sleep` with either exactly 1 positional argument '
                'or a `seconds` keyword argument, but instead got call signature of `{}`'.format(repr(mock_sleep_call))
            )

        return sleep_seconds

    def test_will_wait_if_runtime_is_less_than_minimum_time(self):
        minimum_time = 5
        waiter = waits.Waiter(minimum_time)
        waiter._start_time = waits.get_time()

        with mock.patch('time.sleep') as mock_sleep:
            waiter.__exit__(None, None, None)

        self.assertEqual(
            1,
            mock_sleep.call_count,
            'Expected `time.sleep` to be called once but was called {} times'.format(mock_sleep.call_count)
        )

        # Extract the `seconds` argument passed to `time.sleep`
        sleep_duration = self._get_seconds_argument_for_mocked_sleep_call(mock_sleep.call_args_list[0])
        self.assertGreater(
            sleep_duration,
            0,
            'Expected a positive sleep duration value but got {}'.format(sleep_duration)
        )

    def test_does_not_raise_exception_if_runtime_is_greater_than_minimum_time(self):
        minimum_time = 5
        waiter = waits.Waiter(minimum_time)
        waiter._start_time = waits.get_time() - minimum_time

        with mock.patch('time.sleep', side_effect=time.sleep) as mock_sleep:
            waiter.__exit__(None, None, None)

        self.assertEqual(
            1,
            mock_sleep.call_count,
            'Expected `time.sleep` to be called once but was called {} times'.format(mock_sleep.call_count)
        )

        # Extract the `seconds` argument passed to `time.sleep`
        sleep_duration = self._get_seconds_argument_for_mocked_sleep_call(mock_sleep.call_args_list[0])
        self.assertLess(
            sleep_duration,
            0,
            'Expected a negative sleep duration value but got {}'.format(sleep_duration)
        )


class ObservableWaiterInitTestCase(unittest.TestCase):
    def test_initial_state(self):
        minimum_time = 5

        waiter = waits.ObservableWaiter(minimum_time)

        self.assertEqual(waiter.minimum_time, minimum_time)
        self.assertIsNone(waiter._start_time)
        self.assertIsNone(waiter.last_runtime)
        self.assertIsNone(waiter.last_elapsed)


class ObservableWaiterExitTestCase(unittest.TestCase):
    def test_records_last_runtime(self):
        waiter = waits.ObservableWaiter(.5)
        sleep_time = .2

        with waiter:
            time.sleep(sleep_time)
        end = waits.get_time()

        self.assertAlmostEqual(sleep_time, waiter.last_runtime, delta=end - waiter._start_time)

    def test_records_last_elapsed(self):
        waiter = waits.ObservableWaiter(.1)

        start = waits.get_time()
        with waiter:
            pass
        end = waits.get_time()

        # We expect the elapsed time of our waiter to be greater than the waiter's minimum time
        # and less than the time elapsed between entering and exiting the context manager
        self.assertGreater(waiter.last_elapsed, waiter.minimum_time)
        self.assertLess(waiter.last_elapsed, end - start)
