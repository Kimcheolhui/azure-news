"""Tests for analysis.utils.json_parser.extract_json."""

from analysis.utils.json_parser import extract_json


class TestExtractJsonDirect:
    """Strategy 1: Direct JSON parsing."""

    def test_valid_json_object(self):
        text = '{"key": "value", "num": 42}'
        assert extract_json(text) == {"key": "value", "num": 42}

    def test_valid_json_nested(self):
        text = '{"outer": {"inner": [1, 2, 3]}}'
        result = extract_json(text)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_json_array_returns_none(self):
        """extract_json expects a dict, not a list."""
        text = '[1, 2, 3]'
        assert extract_json(text) is None

    def test_empty_object(self):
        assert extract_json("{}") == {}


class TestExtractJsonFenced:
    """Strategy 2: Markdown fenced code blocks."""

    def test_json_fence(self):
        text = 'Here is the result:\n```json\n{"status": "ok"}\n```\nDone.'
        assert extract_json(text) == {"status": "ok"}

    def test_plain_fence(self):
        text = '```\n{"status": "ok"}\n```'
        assert extract_json(text) == {"status": "ok"}

    def test_fence_with_extra_whitespace(self):
        text = '```json\n  {"status": "ok"}  \n```'
        assert extract_json(text) == {"status": "ok"}


class TestExtractJsonBraceSlice:
    """Strategy 3: First '{' to last '}'."""

    def test_json_with_surrounding_text(self):
        text = 'The analysis is: {"type": "update"} as shown above.'
        assert extract_json(text) == {"type": "update"}

    def test_json_with_preamble(self):
        text = 'Sure! Here is the JSON:\n\n{"update_type": "ga", "services": ["AKS"]}'
        result = extract_json(text)
        assert result["update_type"] == "ga"
        assert result["services"] == ["AKS"]


class TestExtractJsonFailures:
    """Cases where all strategies fail."""

    def test_empty_string(self):
        assert extract_json("") is None

    def test_no_json(self):
        assert extract_json("This is just plain text.") is None

    def test_malformed_json(self):
        assert extract_json("{broken: json}") is None

    def test_none_input(self):
        assert extract_json(None) is None

    def test_incomplete_json(self):
        assert extract_json('{"key": "value"') is None


class TestExtractJsonRealWorld:
    """Realistic LLM response patterns."""

    def test_analysis_response(self):
        text = """Based on my analysis, here are the results:

```json
{
    "update_type": "new_feature",
    "affected_services": ["Azure Kubernetes Service"],
    "impact_summary": "New autoprovision capability",
    "key_details": ["Auto node creation"],
    "action_items": ["Test in staging"]
}
```

Let me know if you need more details."""
        result = extract_json(text)
        assert result is not None
        assert result["update_type"] == "new_feature"
        assert len(result["affected_services"]) == 1

    def test_writing_response_bilingual(self):
        text = """{
    "title_ko": "AKS 업데이트",
    "title_en": "AKS Update",
    "summary_ko": "요약",
    "summary_en": "Summary",
    "body_ko": "본문",
    "body_en": "Body"
}"""
        result = extract_json(text)
        assert result["title_ko"] == "AKS 업데이트"
        assert result["title_en"] == "AKS Update"
