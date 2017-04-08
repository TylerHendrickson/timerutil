# timerutil
Timerutil is a collection of timer-related utilities for Python.  Chances are, you've used tools like 
these yourself at one point.  This library was born out of a desire to avoid needing to reimplement 
various time-related functionality throughout various Python code bases.  Maybe you'll find it similarly 
useful as well!

Specifically, this library provides the following:
- `TimeoutManager`: A context manager/decorator for enforcing timeouts around operations
- `Waiter`: A context manager/decorator which enforces a minimum time restriction on wrapped operations


## `TimeoutManager`
This class acts as a simple context manager or decorator for enforcing timeouts around operations.

### Basic Usage
#### As a context manager
```python
with TimeoutManager(10):
    something_that_should_not_exceed_ten_seconds()
```

#### As a decorator
```python
@TimeoutManager(10)
def something_that_should_not_exceed_ten_seconds():
    print("If you can't read this, you're under some heavy load.")
```

#### Customize `TimeoutError` messages
By default, `TimeoutError` are raised by `TimeoutManager` with the platform-specific message 
corresponding to the `ETIME` error number.  If you want something more specific for your use-case,
you can provide one during initialization.
```python
with TimeoutManager(10, timeout_message='Houston, we have a timeout'):
    something_that_should_not_exceed_ten_seconds()
```

#### Suppress `TimeoutError`s from being raised when the timer expires
Sometimes you don't care if when timeouts occur- maybe it's not important enough to interrupt your application.
In these cases, you can configure `TimeoutManager` to suppress timeout errors so that wrapped operations 
will fail silently if they exceed your configured duration.
```python
with TimeoutManager(10, suppress_timeout_errors=True):
    something_that_should_not_exceed_ten_seconds()
print('Maybe exceeded 10 seconds, but no longer executing either way')
```

## Compatibility Notes
- This package has been tested compatible with Python versions 2.7 to 3.6.
- As `TimeoutManager` makes use of signals, this utility will not work on Windows platforms.
- Systems running versions of Python < 3.3 do not have a builtin `TimeoutError` exception class.
In these cases, the custom `timerutil.exc.TimeoutError` exception will be used instead.
- The `contextlib` package in versions of Python < 3.2 does not provide the `ContextDecorator` class.
In these cases, the `timerutil` library will substitute a version of this class (backported from Python 3.4) 
when defining context manager/decorator utilities.
