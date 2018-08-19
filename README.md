# timerutil

![Travis CI build status](https://img.shields.io/travis/TylerHendrickson/timerutil.svg)
![Codecov coverage report](https://img.shields.io/codecov/c/github/sgrepo/celery-unique.svg)

Timerutil is a collection of timer-related utilities for Python.  Chances are, you've used tools like 
these yourself at one point.  This library was born out of a desire to avoid needing to reimplement 
various time-related functionality throughout various Python code bases.  Maybe you'll find it similarly 
useful as well!

Specifically, this library provides the following:
- `TimeoutManager`: A context manager/decorator for enforcing timeouts around operations
- `Waiter`: A context manager/decorator which enforces a minimum time restriction on wrapped operations


## `timerutil.TimeoutManager`

This class acts as a simple context manager or decorator for enforcing timeouts around operations.


### Basic Usage


#### As a context manager

```python
from timerutil import TimeoutManager

with TimeoutManager(10):
    something_that_should_not_exceed_ten_seconds()
```


#### As a decorator

```python
from timerutil import TimeoutManager

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


#### Suppress `TimeoutError` exceptions

Sometimes you don't care if when timeouts occur- maybe it's not important enough to interrupt your application.
In these cases, you can configure `TimeoutManager` to suppress timeout errors so that wrapped operations 
will fail silently if they exceed your configured duration.

```python
with TimeoutManager(10, suppress_timeout_errors=True):
    something_that_should_not_exceed_ten_seconds()
print('Maybe exceeded 10 seconds, but no longer executing either way')
```

## `timerutil.Waiter`

Another context manager/decorator class for enforcing a minimum execution time on wrapped code.
This is useful if you're fairly confident that your function should finish in a certain amount of time,
but you want to make the return time constant (e.g. to prevent constant-time attacks).


### Basic Usage


#### As a decorator:

```python
from timerutil import Waiter

@Waiter(10)
def take_ten():
    print('Starting to wait')

take_ten()
# Ten seconds later...
print('Done waiting!')
```


#### As a context manager:

```python
with Waiter(10):
    print('Starting to wait')

# Ten seconds later...
print('Done waiting!')
```

## Other `Waiter` implementations

The `timerutil.waits` module provides a few additional implementations of the `Waiter` class that may be useful
in certain particular scenarios.


### `timerutil.waits.ObservableWaiter`

This `Waiter` subclass which behaves exactly the same as its parent, except that it records usage statistics
for inspection. This also be used as a context manager or a decorator.

```python
with ObservableWaiter(10) as ten_second_waiter:
    print('Starting to wait')

print(
    'Done waiting after',
    ten_second_waiter.last_elapsed,
    'seconds'
)
```


### `timerutil.waits.StopWatch`

A subclass of `ObservableWaiter`, this implementation doesn't actually enforce any minimum execution time. Therefore,
it is especially useful as a way to time wrapped code execution without impacting its behavior or extending its
execution time. Use this for easily logging execution time in Production when solutions like `timeit` are impractical.

```python
with StopWatch() as stop_watch:
    watch_this()

logging.log(logging.INFO, 'Watched watch_this() do some things for %r seconds', timer.last_runtime)
```


#### Extending for Logging

When subclassed, you can override the `StopWatch.__exit__` method to add behaviors for automatically capturing
execution time for your wrapped code- just be sure to call `super()`!

```python
class LoggingStopWatch(StopWatch):
    def __exit__(self, exc_type, exc_val, exc_tb):
        rv = super(LoggingStopWatch, self).__exit__()
        my_logger.info('Finished executing after %r seconds' % self.last_runtime)
        return rv
```


## Compatibility Notes

- This package has been tested compatible with Python versions 2.7 to 3.7
- As `TimeoutManager` makes use of signals, this utility will not work on Windows platforms
- Systems running versions of Python < 3.3 do not have a builtin `TimeoutError` exception class.
In these cases, a custom `TimeoutError` exception will be used instead.
- The `contextlib` package in versions of Python < 3.2 does not provide the `ContextDecorator` class.
In these cases, the `timerutil` library will substitute a version of this class (backported from Python 3.4) 
when defining context manager/decorator utilities.
