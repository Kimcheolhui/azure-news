"""Tests for analysis.pipeline.deep_scraper."""

from unittest.mock import patch, MagicMock

import requests

from analysis.pipeline.deep_scraper import scrape_full_content


class TestScrapeFullContentSuccess:
    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_returns_text_on_success(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><p>Article content here</p></body></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = scrape_full_content("https://example.com/article")

        assert result["url"] == "https://example.com/article"
        assert "Article content here" in result["text"]
        assert "error" not in result
        assert isinstance(result["raw_length"], int)
        assert isinstance(result["truncated"], bool)

    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_truncates_long_content(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<p>" + "x" * 20000 + "</p>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = scrape_full_content("https://example.com/long")
        assert result["truncated"] is True
        assert "[Content truncated]" in result["text"]


class TestScrapeFullContentRetry:
    @patch("analysis.pipeline.deep_scraper.time.sleep")
    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_retries_on_transient_status(self, mock_get, mock_sleep):
        fail_resp = MagicMock()
        fail_resp.status_code = 503

        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.text = "<p>Recovered</p>"
        ok_resp.raise_for_status = MagicMock()

        mock_get.side_effect = [fail_resp, ok_resp]

        result = scrape_full_content("https://example.com/retry")
        assert "Recovered" in result["text"]
        assert mock_get.call_count == 2

    @patch("analysis.pipeline.deep_scraper.time.sleep")
    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_retries_on_connection_error(self, mock_get, mock_sleep):
        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.text = "<p>OK</p>"
        ok_resp.raise_for_status = MagicMock()

        mock_get.side_effect = [
            requests.exceptions.ConnectionError("refused"),
            ok_resp,
        ]

        result = scrape_full_content("https://example.com/connfail")
        assert "OK" in result["text"]

    @patch("analysis.pipeline.deep_scraper.time.sleep")
    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_retries_on_timeout(self, mock_get, mock_sleep):
        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.text = "<p>OK</p>"
        ok_resp.raise_for_status = MagicMock()

        mock_get.side_effect = [
            requests.exceptions.Timeout("timed out"),
            ok_resp,
        ]

        result = scrape_full_content("https://example.com/timeout")
        assert "OK" in result["text"]


class TestScrapeFullContentFailure:
    @patch("analysis.pipeline.deep_scraper.time.sleep")
    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_all_retries_exhausted(self, mock_get, mock_sleep):
        fail_resp = MagicMock()
        fail_resp.status_code = 500

        mock_get.return_value = fail_resp

        result = scrape_full_content("https://example.com/fail")
        assert result["error"] == "HTTP 500"
        assert result["text"] == ""
        # 1 initial + 2 retries = 3 calls
        assert mock_get.call_count == 3

    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_non_transient_error_no_retry(self, mock_get):
        mock_get.side_effect = requests.exceptions.InvalidURL("bad url")

        result = scrape_full_content("not-a-url")
        assert "error" in result
        assert result["text"] == ""
        assert mock_get.call_count == 1

    @patch("analysis.pipeline.deep_scraper.requests.get")
    def test_http_404_no_retry(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        mock_get.return_value = mock_resp

        result = scrape_full_content("https://example.com/missing")
        assert "error" in result
        assert mock_get.call_count == 1
