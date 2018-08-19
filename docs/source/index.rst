Welcome to timerutil!
=====================================

Timerutil is a collection of timer-related utilities for Python.  Chances are, you've used tools like
these yourself at one point.  This library was born out of a desire to avoid needing to reimplement
various time-related functionality throughout various Python code bases.  Maybe you'll find it similarly
useful as well!

Specifically, this library provides the following tools:

- :class:`~timerutil.timeouts.TimeoutManager`: A context manager/decorator for enforcing timeouts around operations
- :class:`~timerutil.waits.Waiter`: A context manager/decorator which enforces a minimum time restriction on wrapped operations
- :class:`~timerutil.waits.ObservableWaiter`: A :class:`~timerutil.waits.Waiter` implementation that records execution time
for wrapped operations


#################
Table of Contents
#################

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Utilities for Timeouts <timerutil/timeouts.rst>
   Utilities for Waiting <timerutil/waits.rst>
   Compatibility Resources <timerutil/compat.rst>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
