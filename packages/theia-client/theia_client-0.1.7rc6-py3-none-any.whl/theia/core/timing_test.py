import math

import pytest

from theia.core import test_mocks, timing

_TIMEOUT_S = 10


def test_timer_no_duration() -> None:
    with test_mocks.mock_time(0):
        timer = timing.Timer()
    with test_mocks.mock_time(1):
        assert timer.elapsed_s() == 1.0
    with pytest.raises(ValueError):
        timer.is_finished()


def test_timer_duration() -> None:
    with test_mocks.mock_time(0):
        timer = timing.Timer(_TIMEOUT_S)
        assert not timer.is_finished()
    with test_mocks.mock_time(_TIMEOUT_S / 2):
        assert not timer.is_finished()
    with test_mocks.mock_time(2 * _TIMEOUT_S):
        assert timer.is_finished()


def test_frequency_counter_not_started() -> None:
    """Test that FrequencyCounter is not ready and returns 0 for rate and count if
    update is never called.
    """
    counter = timing.FrequencyCounter(_TIMEOUT_S)
    with test_mocks.mock_time(0):
        assert counter.frequency() == 0
    with test_mocks.mock_time(_TIMEOUT_S * 2):
        assert counter.frequency() == 0


def test_frequency_counter_update() -> None:
    counter = timing.FrequencyCounter(_TIMEOUT_S)
    with test_mocks.mock_time(0):
        counter.update()
    with test_mocks.mock_time(0.25 * _TIMEOUT_S):
        freq = counter.frequency()
        expected_freq = 1 / _TIMEOUT_S
        assert math.isclose(freq, expected_freq, abs_tol=1e-5)
        counter.update()
    with test_mocks.mock_time(0.75 * _TIMEOUT_S):
        freq = counter.frequency()
        expected_freq = 2 / _TIMEOUT_S
        assert math.isclose(freq, expected_freq, abs_tol=1e-5)
        counter.update()
    with test_mocks.mock_time(_TIMEOUT_S):
        freq = counter.frequency()
        expected_freq = 2 / _TIMEOUT_S
        assert math.isclose(freq, expected_freq, abs_tol=1e-5)


def test_expiring_queue_expiration() -> None:
    with test_mocks.mock_time(0):
        expiring_q = timing.ExpiringQueue[int](2)
    with test_mocks.mock_time(1):
        expiring_q.append(1)
        expiring_q.append(2)
        assert expiring_q.values() == [1, 2]
    with test_mocks.mock_time(2):
        expiring_q.append(1)
        assert expiring_q.values() == [1, 2, 1]
    with test_mocks.mock_time(3):
        assert expiring_q.values() == [1]
    with test_mocks.mock_time(4):
        assert expiring_q.values() == []


def test_expiring_dict_expiration() -> None:
    with test_mocks.mock_time(0):
        expiring_dict = timing.ExpiringDict[str, int](2)
    with test_mocks.mock_time(1):
        expiring_dict.set("A", 1)
        expiring_dict.set("B", 2)
        assert dict(expiring_dict.items()) == {"A": 1, "B": 2}
    with test_mocks.mock_time(2):
        expiring_dict.set("A", 3)
        assert dict(expiring_dict.items()) == {"A": 3, "B": 2}
    with test_mocks.mock_time(3):
        assert dict(expiring_dict.items()) == {"A": 3}
    with test_mocks.mock_time(4):
        assert dict(expiring_dict.items()) == {}
    with test_mocks.mock_time(5):
        expiring_dict.set("A", 1)
        expiring_dict.delete("B")
        assert dict(expiring_dict.items()) == {"A": 1}
        expiring_dict.delete("A")
        assert dict(expiring_dict.items()) == {}


def test_expiring_set_expiration() -> None:
    with test_mocks.mock_time(0):
        expiring_set = timing.ExpiringSet[int](2)
    with test_mocks.mock_time(1):
        expiring_set.add(1)
        expiring_set.add(2)
        assert expiring_set.values() == {1, 2}
    with test_mocks.mock_time(2):
        expiring_set.add(1)
        assert expiring_set.values() == {1, 2}
    with test_mocks.mock_time(3.5):
        assert expiring_set.values() == {1}
