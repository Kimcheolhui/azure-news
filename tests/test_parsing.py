"""Tests for ingest.utils.parsing."""

from datetime import datetime, timezone

from ingest.utils.parsing import parse_datetime, strip_html


class TestStripHtml:
    def test_basic_tags(self):
        assert strip_html("<p>Hello</p>") == "Hello"

    def test_nested_tags(self):
        result = strip_html("<div><p>Hello <b>world</b></p></div>")
        assert "Hello" in result
        assert "world" in result

    def test_empty_string(self):
        assert strip_html("") == ""

    def test_plain_text(self):
        assert strip_html("no tags here") == "no tags here"

    def test_entities(self):
        result = strip_html("<p>A &amp; B</p>")
        assert "A" in result and "B" in result


class TestParseDatetime:
    def test_none_input(self):
        assert parse_datetime(None) is None

    def test_empty_string(self):
        assert parse_datetime("") is None

    def test_rfc2822(self):
        """RSS feeds commonly use RFC-2822 dates."""
        result = parse_datetime("Mon, 20 Mar 2026 12:00:00 GMT")
        assert result is not None
        assert result.year == 2026
        assert result.month == 3
        assert result.day == 20
        assert result.tzinfo is not None

    def test_iso8601(self):
        result = parse_datetime("2026-03-20T12:00:00+00:00")
        assert result is not None
        assert result.year == 2026

    def test_iso8601_naive_gets_utc(self):
        """Naive ISO datetimes should get UTC timezone."""
        result = parse_datetime("2026-03-20T12:00:00")
        assert result is not None
        assert result.tzinfo is not None

    def test_fuzzy_date(self):
        result = parse_datetime("March 20, 2026")
        assert result is not None
        assert result.year == 2026
        assert result.month == 3

    def test_invalid_string(self):
        assert parse_datetime("not a date at all xyz") is None

    def test_result_is_utc_aware(self):
        result = parse_datetime("2026-01-01")
        assert result is not None
        assert result.tzinfo is not None
