try:
    from contextlib import ContextDecorator
except ImportError:  # pragma: nocover
    # Re-implement the `ContextDecorator` class added in Python 3.2
    from functools import wraps


    class ContextDecorator(object):
        """A base class or mixin that enables context managers to work as decorators.

        Note: This class has been reimplemented from Python 3.4.3
            in order to maintain compatibility with versions of Python (before 3.2)
            where `contextlib.ContextDecorator` does not exist.
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
