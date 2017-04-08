try:
    TimeoutError = TimeoutError
except NameError:  # pragma: nocover
    class TimeoutError(OSError):
        pass
