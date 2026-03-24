"""Tests for analysis.pipeline.writer."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from analysis.pipeline.writer import write_report


class TestWriteReport:
    @pytest.mark.asyncio
    @patch("analysis.pipeline.writer.analysis_session")
    @patch("analysis.pipeline.writer.send_message")
    async def test_returns_bilingual_report(
        self, mock_send, mock_session_ctx, sample_update, sample_analysis_data,
    ):
        report_json = {
            "title_ko": "AKS 업데이트",
            "title_en": "AKS Update",
            "summary_ko": "요약",
            "summary_en": "Summary",
            "body_ko": "본문",
            "body_en": "Body",
        }
        mock_send.return_value = json.dumps(report_json, ensure_ascii=False)

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await write_report(sample_update, sample_analysis_data)

        assert result["title_ko"] == "AKS 업데이트"
        assert result["title_en"] == "AKS Update"
        assert result["summary_ko"] == "요약"
        assert result["summary_en"] == "Summary"
        assert result["body_ko"] == "본문"
        assert result["body_en"] == "Body"
        assert "raw_response" in result

    @pytest.mark.asyncio
    @patch("analysis.pipeline.writer.analysis_session")
    @patch("analysis.pipeline.writer.send_message")
    async def test_handles_markdown_fenced_response(
        self, mock_send, mock_session_ctx, sample_update, sample_analysis_data,
    ):
        response = """Here is the report:
```json
{
    "title_ko": "제목",
    "title_en": "Title",
    "summary_ko": "요약",
    "summary_en": "Summary",
    "body_ko": "본문",
    "body_en": "Body"
}
```
Done!"""
        mock_send.return_value = response

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await write_report(sample_update, sample_analysis_data)
        assert result["title_ko"] == "제목"
        assert result["title_en"] == "Title"

    @pytest.mark.asyncio
    @patch("analysis.pipeline.writer.analysis_session")
    @patch("analysis.pipeline.writer.send_message")
    async def test_handles_parse_failure(
        self, mock_send, mock_session_ctx, sample_update, sample_analysis_data,
    ):
        mock_send.return_value = "completely unparseable response"

        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await write_report(sample_update, sample_analysis_data)
        assert "parse_error" in result
        assert result["title_ko"] == ""
        assert result["title_en"] == ""
        assert "raw_response" in result
