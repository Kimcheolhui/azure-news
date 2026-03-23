"""Tests for analysis.pipeline.analyzer."""

import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from analysis.pipeline.analyzer import analyze_update, _format_related_updates, _build_content


class TestFormatRelatedUpdates:
    def test_empty_list(self):
        assert _format_related_updates({"related_updates": []}) == "None found."

    def test_missing_key(self):
        assert _format_related_updates({}) == "None found."

    def test_formats_entries(self):
        data = {
            "related_updates": [
                {
                    "title": "AKS Update",
                    "published_date": "2026-03-15",
                    "source_url": "https://example.com",
                    "summary": "Some summary",
                },
            ]
        }
        result = _format_related_updates(data)
        assert "AKS Update" in result
        assert "2026-03-15" in result
        assert "https://example.com" in result
        assert "Some summary" in result


class TestBuildContent:
    def test_uses_scraped_text(self, sample_update):
        content = {"text": "Scraped article text"}
        assert _build_content(sample_update, content) == "Scraped article text"

    def test_falls_back_to_update_summary(self, sample_update):
        content = {"error": "HTTP 500", "text": ""}
        result = _build_content(sample_update, content)
        assert sample_update.summary in result

    def test_falls_back_to_update_body(self, sample_update):
        sample_update.summary = None
        content = {"text": ""}
        result = _build_content(sample_update, content)
        assert sample_update.body in result

    def test_no_content_available(self, sample_update):
        sample_update.summary = None
        sample_update.body = None
        content = {"text": ""}
        assert _build_content(sample_update, content) == "(No content available.)"


class TestAnalyzeUpdate:
    @pytest.mark.asyncio
    @patch("analysis.pipeline.analyzer.analysis_session")
    @patch("analysis.pipeline.analyzer.send_message")
    async def test_returns_parsed_analysis(
        self, mock_send, mock_session_ctx,
        sample_update, sample_scraped_content, sample_research_data,
    ):
        analysis_json = {
            "update_type": "new_feature",
            "affected_services": ["AKS"],
            "impact_summary": "New feature added.",
            "key_details": ["Detail 1"],
            "action_items": ["Action 1"],
        }
        mock_send.return_value = json.dumps(analysis_json)

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await analyze_update(
            sample_update, sample_scraped_content, sample_research_data,
        )
        assert result["update_type"] == "new_feature"
        assert result["affected_services"] == ["AKS"]
        assert "raw_response" in result

    @pytest.mark.asyncio
    @patch("analysis.pipeline.analyzer.analysis_session")
    @patch("analysis.pipeline.analyzer.send_message")
    async def test_handles_json_parse_failure(
        self, mock_send, mock_session_ctx,
        sample_update, sample_scraped_content, sample_research_data,
    ):
        mock_send.return_value = "This is not JSON at all"

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await analyze_update(
            sample_update, sample_scraped_content, sample_research_data,
        )
        assert "parse_error" in result
        assert result["update_type"] == "update"  # default fallback
        assert result["affected_services"] == []
