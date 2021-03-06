"""This module provides decorator/context manager solutions that prevent wrapped operations from finishing
before a given number of seconds has elapsed.

Useful if you're fairly confident that your function should finish in a certain amount of time,
but you want to make the return time constant (e.g. to prevent constant-time attacks).

For example, if we know that our password reset function consistently takes about 1 second to execute
if the given email address is valid but if the email address is invalid, it usually finishes much faster,
We can ensure that it always takes 2 seconds to execute whenever it's called.

This is less useful if your function's normal execution time is subject to a lot of jitter.
"""
import time

from timerutil.compat import (
    ContextDecorator,
    get_time
)

__all__ = [
    'ObservableWaiter',
    'StopWatch',
    'Waiter'
]


class Waiter(ContextDecorator):
    """Context manager/decorator which prevents an operation
    from finishing before a given number of seconds has elapsed.

    Usage as a decorator:
        .. code-block:: python

            @Waiter(10)
            def take_ten():
                print('Starting to wait')

            take_ten()
            # Ten seconds later...
            print('Done waiting!')

    Usage as a context manager:
        .. code-block:: python

            with Waiter(10):
                print("Starting to wait")

            # Ten seconds later...
            print("Done waiting!")
    """

    def __init__(self, minimum_time):
        """Initializes a Waiter

        :param minimum_time: The number of seconds that must elapse before the Waiter exits
        :type minimum_time: int, float
        """
        super(ContextDecorator, self).__init__()
        self.minimum_time = minimum_time
        self._start_time = None

    def __enter__(self):
        """Begins a countdown for the configured duration

        :return: This :class:`~Waiter` instance
        :rtype: Waiter
        """
        self._start_time = get_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Blocks until the configured duration has elapsed
        """
        try:
            time.sleep(self.minimum_time - (get_time() - self._start_time))
        except (ValueError, IOError):
            pass


class ObservableWaiter(Waiter):
    """A :class:`~Waiter` subclass which behaves exactly the same as its parent,
    except that it records usage statistics for inspection.

    :ivar last_runtime: The total duration of the last wrapped operation, in seconds
    :vartype last_runtime: float
    :ivar last_elapsed: The total duration that the decorator/context manager was active, in seconds.
        This should always be greater than or (rarely) equal to :attr:`~last_runtime`.
    :vartype last_elapsed: float

    Usage as a decorator:
        .. code-block:: python

            ten_second_waiter = ObservableWaiter(10)

            @ten_second_waiter
            def take_ten():
                print('Starting to wait')

            >>> take_ten()
            >>> print(
            ...     'Call to take_ten() finished after:\\n',
            ...     ten_second_waiter.last_runtime,
            ...     'seconds'
            ... )
            Call to take_ten() finished after
            2.366909757256508e-05 seconds
            >>> print(
            ...     'Total time with waiter:',
            ...     ten_second_waiter.last_elapsed,
            ...     'seconds'
            ... )
            Total time with waiter: 10.003751991083845 seconds

    Usage as a context manager:
        .. code-block:: python

            with ObservableWaiter(10) as ten_second_waiter:
                print('Starting to wait')

            print(
                'Done waiting after',
                ten_second_waiter.last_elapsed,
                'seconds'
            )
    """

    def __init__(self, minimum_time):
        super(ObservableWaiter, self).__init__(minimum_time)
        self.last_runtime = None
        self.last_elapsed = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Record the approximate runtime of the wrapped operation
        self.last_runtime = get_time() - self._start_time

        super(ObservableWaiter, self).__exit__(exc_type, exc_val, exc_tb)

        # Record the duration of time since `__enter__` began
        self.last_elapsed = get_time() - self._start_time


class StopWatch(ObservableWaiter):
    """Context manager/decorator for observing the execution time of wrapped operations, but without enforcing
    a minimum time (a stopwatch!). Useful in cases where :mod:`timeit` is impractical or overcomplicated.

    .. note:: This class is mostly provided out of convenience (primarily for DRYness and readability),
        since a correctly-configured instance of :class:`ObservableWaiter` could achieve the same behavior.
        As this class is an implementation of :class:`ObservableWaiter`, it provides the same interface for
        inspecting statistics. The only effective difference is that this Waiter does not enforce any
        minimum execution time.

    Example of observing the execution time for a function call by using this class as a decorator:
        .. code-block:: python

            timer = StopWatch()

            @timer
            def watch_this():
                # Do some things
                ...

            watch_this()
            logging.log(logging.INFO, 'Watched watch_this() do some things for %r seconds', timer.last_runtime)

    Example of observing the execution time of nested code by using this class as a context manager:
        .. code-block:: python

            with StopWatch() as timer:
                # Do some things
                ...

            logging.log(logging.INFO, 'Watched some things for %r seconds', timer.last_runtime)

    """
    def __init__(self):
        """Initializes a StopWatch for observing the execution time of wrapped operations"""
        super(StopWatch, self).__init__(0)

    def __setattr__(self, name, value):
        """Prevents the :attr:`minimum_time` attribute from being set to a nonzero value.

        :raises AttributeError: If the :attr:`minimum_value` instance attribute is being set
            to any value other than zero
        """
        if name == 'minimum_time' and value != 0:
            raise AttributeError('minimum_time attribute is read-only')
        super(StopWatch, self).__setattr__(name, value)
