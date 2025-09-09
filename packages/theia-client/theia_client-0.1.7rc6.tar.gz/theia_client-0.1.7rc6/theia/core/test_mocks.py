"""Test mocking utilities for core functionality."""

import contextlib
from typing import Generator
from unittest import mock


def _mock_time_time(time_s: float) -> mock._patch:
    """Monkeypatches time.time() to return the given time.

    Should be used as a context manager.
    """
    return mock.patch("time.time", mock.MagicMock(return_value=time_s))


def _mock_time_perf_counter(time_s: float) -> mock._patch:
    """Monkeypatches time.perf_counter() to return the given time. Since
    time.perf_counter() is used inside Timer, this mocks the time measured by Timer.

    Should be used as a context manager.
    """
    return mock.patch("time.perf_counter", mock.MagicMock(return_value=time_s))


@contextlib.contextmanager
def mock_time(time_s: float) -> Generator[None, None, None]:
    """Mocks the flow of time reported by time.perf_counter() and time.time()."""
    with _mock_time_perf_counter(time_s), _mock_time_time(time_s):
        yield
