try:
    TimeoutError = TimeoutError
except NameError:
    class TimeoutError(OSError):
        pass
