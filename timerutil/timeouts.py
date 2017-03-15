import contextlib
import errno
import os
import signal

from timerutil.exc import TimeoutError


try:
    DEFAULT_TIMEOUT_MESSAGE = os.strerror(errno.ETIME)
except ValueError:
    DEFAULT_TIMEOUT_MESSAGE = 'Timer Expired'


class TimeoutManager(contextlib.ContextDecorator):
    """A class for easily putting time restrictions on things

    Usage as a context manager:
    >>> import time
    >>> with TimeoutManager(10):
    >>>     something_that_should_not_exceed_ten_seconds()

    Usage as a decorator:
    >>> @TimeoutManager(10)
    >>> def something_that_should_not_exceed_ten_seconds():
    >>>     time.sleep(5)

    Handle timeouts:
    >>> try:
    >>>     with TimeoutManager(10):
    >>>         something_that_should_not_exceed_ten_seconds()
    >>> except TimeoutError:
    >>>     print("Got a timeout, couldn't finish")

    Suppress TimeoutError and just die after expiration:
    >>> with TimeoutManager(10, suppress_timeout_errors=True):
    >>>     something_that_should_not_exceed_ten_seconds()
    >>> print('Maybe exceeded 10 seconds, but no longer executing either way')
    """

    def __init__(self, seconds, timeout_message=os.strerror(errno.ETIME), suppress_timeout_errors=False):
        """Initializes and configures a new TimeoutManager

        :param seconds: The number of seconds after which the managed operation should time out
        :type seconds: int
        :param timeout_message: (Optional) Message provided when a `TimeoutError` is raised.
            Defaults to DEFAULT_TIMEOUT_MESSAGE defined by this module.
        :type timeout_message: str
        :param suppress_timeout_errors: (Optional) If True, operations which have timed out will silently fail.
            Defaults to False so that timeouts will result in a `TimeoutError` being raised.
        :type suppress_timeout_errors: bool
        """
        self.seconds = int(seconds)
        self.timeout_message = timeout_message
        self.suppress = bool(suppress_timeout_errors)

    def _timeout_handler(self, signum, frame):
        """Raises a `TimeoutError` with the configured message
        """
        raise TimeoutError(self.timeout_message)

    def __enter__(self):
        """Starts the timeout countdown
        """
        # Save the current SIGALRM handler to restore upon exiting
        self._original_alarm_handler = signal.signal(signal.SIGALRM, self._timeout_handler)

        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ends the timeout countdown, either because the operation has finished
        or because the operation timed out.

        This method will allow a `TimeoutError` raised during the operation to propagate
        unless this `TimeoutManager` instance was configured to suppress `TimeoutError` exceptions.
        """
        # Restore the SIGALRM handler
        signal.signal(signal.SIGALRM, self._original_alarm_handler)
        signal.alarm(0)

        if self.suppress and exc_type is TimeoutError:
            # Suppress the `TimeoutError` so that the timeout is silenced
            return True
