"""
This module provides simple decorator/context manager that prevents an operations from finishing
before a given number of seconds has elapsed.

Useful if you're fairly confident that your function should finish in a certain amount of time,
but you want to make the return time constant (eg. to prevent constant-time attacks).

For example, if we know that our password reset function always takes about 1 second to execute
if the given email address is valid but if the email address is invalid, it usually finishes much faster,
We can ensure that it always takes 2 seconds to execute whenever it's called.

This is less useful if your function's normal execution time is subject to a lot of jitter.
"""
import contextlib
import time


try:
    get_time = time.monotonic
except AttributeError:  # pragma: nocover
    get_time = time.time


class Waiter(contextlib.ContextDecorator):
    """Context manager/decorator which prevents an operation
    from finishing before a given number of seconds has elapsed.
    """

    def __init__(self, minimum_time):
        """Initializes a Waiter

        :param minimum_time: The number of seconds that must elapse before the Waiter exits
        :type minimum_time: int, float
        """
        self.minimum_time = minimum_time
        self.start_time = None

    def __enter__(self):
        """Begins a countdown for the configured duration

        :return: This Waiter instance
        :rtype: Waiter
        """
        self.start_time = get_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Blocks until the configured duration has elapsed
        """
        try:
            time.sleep(self.minimum_time - (get_time() - self.start_time))
        except ValueError:
            pass


class StatWaiter(Waiter):
    """A Waiter subclass which behaves exactly the same as its parent except that it records statistics
    for inspection.

    Recorded metrics are available via the following instance attributes:
        - `last_runtime`: The total duration of the last wrapped operation, in seconds.
        - `last_elapsed`: The total duration that the decorator/context manager was active, in seconds.
            Note: This should always be greater than or equal to `last_runtime`.
    """

    def __init__(self, minimum_time):
        super(StatWaiter, self).__init__(minimum_time)
        self.last_runtime = None
        self.last_elapsed = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Record the approximate runtime of the wrapped operation
        self.last_runtime = get_time() - self.start_time

        super(StatWaiter, self).__exit__(exc_type, exc_val, exc_tb)

        # Record the duration of time since `__enter__` began
        self.last_elapsed = get_time() - self.start_time
