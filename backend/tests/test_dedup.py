"""Tests for ingest.utils.dedup."""

from unittest.mock import MagicMock, patch

from ingest.utils.dedup import is_duplicate, find_existing_urls


class TestIsDuplicate:
    def test_url_in_set(self):
        existing = {"https://example.com/a", "https://example.com/b"}
        assert is_duplicate("https://example.com/a", existing) is True

    def test_url_not_in_set(self):
        existing = {"https://example.com/a"}
        assert is_duplicate("https://example.com/c", existing) is False

    def test_empty_set(self):
        assert is_duplicate("https://example.com", set()) is False


class TestFindExistingUrls:
    def test_empty_urls_returns_empty_set(self):
        mock_session = MagicMock()
        result = find_existing_urls(mock_session, [])
        assert result == set()
        mock_session.query.assert_not_called()

    @patch("ingest.utils.dedup.Update")
    def test_returns_matching_urls(self, mock_update_cls):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [
            ("https://example.com/a",),
            ("https://example.com/c",),
        ]
        urls = ["https://example.com/a", "https://example.com/b", "https://example.com/c"]
        result = find_existing_urls(mock_session, urls)
        assert result == {"https://example.com/a", "https://example.com/c"}

    @patch("ingest.utils.dedup.Update")
    def test_no_matches(self, mock_update_cls):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = []
        result = find_existing_urls(mock_session, ["https://new.com"])
        assert result == set()
