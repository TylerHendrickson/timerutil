"""Provides resources (either builtin, installed, or reimplemented) to maintain compatibility and consistency
across different versions of Python.

.. note:: This module always exports the same interface regardless of the current runtime version.
"""
import time

__all__ = [
    'ContextDecorator',
    'get_time',
    'TimeoutError'
]

try:
    from contextlib import ContextDecorator
except ImportError:  # pragma: nocover
    # Re-implement the `ContextDecorator` class added in Python 3.2
    from functools import wraps


    class ContextDecorator(object):
        """A base class or mixin that enables context managers to work as decorators.

        .. note:: This class is implemented here in order to maintain compatibility
            with versions of Python (before 3.2) where :class:`contextlib.ContextDecorator` does not exist.

            Aside from this docstring, the class implemented here is identical to the implementation
            provided in Python 3.4.3.
        """
        def _recreate_cm(self):
            """Return a recreated instance of self.

            Allows an otherwise one-shot context manager like
            _GeneratorContextManager to support use as
            a decorator via implicit recreation.

            This is a private interface just for _GeneratorContextManager.
            See issue #11647 for details.
            """
            return self

        def __call__(self, func):
            @wraps(func)
            def inner(*args, **kwds):
                with self._recreate_cm():
                    return func(*args, **kwds)

            return inner

try:
    # Prefer using a monotonic clock, if available
    get_time = time.monotonic
except AttributeError:  # pragma: nocover
    get_time = time.time

try:
    # Check if ``TimeoutError`` is a builtin
    TimeoutError = TimeoutError
except NameError:  # pragma: nocover
    # Implement for versions of Python prior to 3.3
    class TimeoutError(OSError):
        """Timeout expired."""
        pass
