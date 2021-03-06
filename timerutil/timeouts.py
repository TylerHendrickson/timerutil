import errno
import os
import signal

from timerutil.compat import (
    ContextDecorator,
    TimeoutError
)

__all__ = ['TimeoutManager']

try:
    # By default, use the platform-specific error message associated with the :attr:`errno.ETIME` symbol
    DEFAULT_TIMEOUT_MESSAGE = os.strerror(errno.ETIME)
except ValueError:  # pragma: nocover
    DEFAULT_TIMEOUT_MESSAGE = 'Timer Expired'


class TimeoutManager(ContextDecorator):
    """A class for easily putting time restrictions on things

    Usage as a context manager:
        .. code-block:: python

            import time
            with TimeoutManager(10):
                something_that_should_not_exceed_ten_seconds()

    Usage as a decorator:
        .. code-block:: python

            @TimeoutManager(10)
            def something_that_should_not_exceed_ten_seconds():
                time.sleep(5)

    Usage for handling timeouts:
        .. code-block:: python

            try:
                with TimeoutManager(10):
                    something_that_should_not_exceed_ten_seconds()
            except TimeoutError:
                print("Got a timeout, couldn't finish")

    As an alternative to raising an exception, you can suppress TimeoutError and just silently end after expiration:
        .. code-block:: python

            with TimeoutManager(10, suppress_timeout_errors=True):
                something_that_should_not_exceed_ten_seconds()

            print('Maybe exceeded 10 seconds')
    """

    def __init__(self, seconds, timeout_message=DEFAULT_TIMEOUT_MESSAGE, suppress_timeout_errors=False):
        """Initializes and configures a new TimeoutManager

        :param seconds: The number of seconds after which the managed operation should time out
        :type seconds: int
        :param timeout_message: (Optional) Message provided when a :exc:`TimeoutError` is raised.
            Defaults to :attr:`~DEFAULT_TIMEOUT_MESSAGE` defined by this module.
        :type timeout_message: str
        :param suppress_timeout_errors: (Optional) If ``True``, operations which have timed out will silently fail.
            Defaults to ``False`` so that timeouts will result in a :exc:`TimeoutError` being raised.
        :type suppress_timeout_errors: bool
        """
        self.seconds = seconds
        self.timeout_message = timeout_message
        self.suppress_errors = bool(suppress_timeout_errors)
        self._original_alarm_handler = None

    def __repr__(self):
        return '<{name}: {seconds} seconds>'.format(name=self.__class__.__name__, seconds=self.seconds)

    def _timeout_handler(self, signum, frame):
        """Raises a :exc:`TimeoutError` with the configured message
        """
        raise TimeoutError(self.timeout_message)

    def __enter__(self):
        """Starts the timeout countdown

        :return: The current instance
        :rtype: TimeoutManager
        """
        # Save the current SIGALRM handler to restore upon exiting
        self._original_alarm_handler = signal.signal(signal.SIGALRM, self._timeout_handler)

        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(self.seconds)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ends the timeout countdown, either because the operation has finished
        or because the operation timed out.

        This method will allow a `TimeoutError` raised during the operation to propagate
        unless this `TimeoutManager` instance was configured to suppress `TimeoutError` exceptions.
        """
        # Restore the SIGALRM handler
        signal.signal(signal.SIGALRM, self._original_alarm_handler)
        signal.alarm(0)

        if self.suppress_errors and exc_type is TimeoutError:
            # Suppress the `TimeoutError` so that the timeout is silenced
            return True
