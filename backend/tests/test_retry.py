"""Tests for ingest.utils.retry.retry_with_backoff."""

import time
from unittest.mock import patch

import pytest

from ingest.utils.retry import retry_with_backoff


class TestRetryWithBackoff:
    def test_succeeds_first_try(self):
        @retry_with_backoff(max_retries=3)
        def always_ok():
            return "ok"

        assert always_ok() == "ok"

    def test_retries_on_failure_then_succeeds(self):
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "done"

        assert fails_twice() == "done"
        assert call_count == 3

    def test_exhausts_retries_then_raises(self):
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            always_fails()

    def test_only_catches_specified_exceptions(self):
        @retry_with_backoff(max_retries=3, exceptions=(ValueError,), base_delay=0.01)
        def raises_type_error():
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            raises_type_error()

    def test_respects_max_retries(self):
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def counting():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            counting()
        # 1 initial + 2 retries = 3 calls
        assert call_count == 3

    @patch("ingest.utils.retry.time.sleep")
    def test_backoff_delays(self, mock_sleep):
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            always_fails()

        delays = [call.args[0] for call in mock_sleep.call_args_list]
        # base_delay * backoff_factor^attempt: 1*2^0=1, 1*2^1=2, 1*2^2=4
        assert delays == [1.0, 2.0, 4.0]

    @patch("ingest.utils.retry.time.sleep")
    def test_max_delay_cap(self, mock_sleep):
        @retry_with_backoff(
            max_retries=3, base_delay=10.0, backoff_factor=10.0, max_delay=50.0,
        )
        def always_fails():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            always_fails()

        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert all(d <= 50.0 for d in delays)
