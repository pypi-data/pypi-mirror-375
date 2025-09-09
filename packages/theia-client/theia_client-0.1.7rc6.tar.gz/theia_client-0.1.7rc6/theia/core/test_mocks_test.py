"""Tests for test mocking utilities."""

import time

from theia.core import test_mocks


def test_mock_time_simple() -> None:
    ts = time.perf_counter()

    with test_mocks.mock_time(0):
        assert time.perf_counter() == 0
        assert time.perf_counter() != ts

    assert ts < time.perf_counter() < ts + 1


def test_mock_time_nested() -> None:
    with test_mocks.mock_time(0):
        assert time.perf_counter() == 0

        with test_mocks.mock_time(1):
            assert time.perf_counter() == 1

        assert time.perf_counter() == 0
