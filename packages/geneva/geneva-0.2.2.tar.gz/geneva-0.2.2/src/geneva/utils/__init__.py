# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# dumping ground for utility functions
from __future__ import annotations

import contextlib
import datetime
import functools
import getpass
import logging
import random
import threading
import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

_LOG = logging.getLogger(__name__)


def retry_on_exception(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Any:
    """
    Decorator to retry a function on exception with exponential backoff.

    :param max_attempts: Total number of attempts (including the first).
    :param initial_delay: Seconds to wait before first retry.
    :param backoff_factor: Multiplier for delay after each failed attempt.
    :param exceptions: Tuple of exception classes to catch and retry on.
    :param warning_message: Template for warning log (see docstring).
    """

    def decorator(func) -> Any:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # noqa: PERF203
                    if attempt >= max_attempts:
                        _LOG.error(
                            f"{func.__name__!r} failed after {attempt} attempts;"
                            " giving up.",
                            exc_info=True,
                        )
                        raise
                    # log the custom warning
                    sleep_time = random.uniform(0, delay)  # jitter
                    _LOG.warning(
                        f"Attempt {attempt} for {func.__name__} failed with {exc!r}; "
                        f"retrying in {sleep_time:.1f}s..."
                    )
                    time.sleep(sleep_time)
                    delay *= backoff_factor
                    attempt += 1

        return wrapper

    return decorator


def dt_now_utc() -> datetime.datetime:
    """Return the current UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)


def current_user() -> str:
    """Return the current user"""
    return getpass.getuser()


class _PeriodicCaller(threading.Thread):
    def __init__(self, fn: Callable[[], None], interval_secs: float) -> None:
        super().__init__(daemon=True)
        self._fn = fn
        self._interval = interval_secs
        self._stop_evt = threading.Event()

    def stop(self) -> None:
        self._stop_evt.set()

    def run(self) -> None:
        # call once immediately for quick “proof of life”, then on the cadence
        with contextlib.suppress(Exception):
            self._fn()

        while not self._stop_evt.wait(self._interval):
            with contextlib.suppress(Exception):
                self._fn()


@contextmanager
def status_updates(
    get_status: Callable[[], None], interval_secs: float
) -> Iterator[None]:
    t = _PeriodicCaller(get_status, interval_secs)
    t.start()
    try:
        yield
    finally:
        t.stop()
        t.join(timeout=5)
