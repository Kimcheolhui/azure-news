"""Tests for analysis.pipeline.researcher.extract_keywords."""

from analysis.pipeline.researcher import extract_keywords


class TestExtractKeywords:
    def test_basic_extraction(self):
        keywords = extract_keywords("Azure Kubernetes Service Update")
        assert "Azure" in keywords
        assert "Kubernetes" in keywords
        assert "Service" in keywords
        assert "Update" in keywords

    def test_filters_stopwords(self):
        keywords = extract_keywords("This is a new update for the service")
        lower_kws = [k.lower() for k in keywords]
        assert "this" not in lower_kws
        assert "the" not in lower_kws
        assert "for" not in lower_kws
        # "update" is in STOPWORDS? No — "new" is in STOPWORDS
        assert "new" not in lower_kws

    def test_strips_punctuation(self):
        keywords = extract_keywords("AKS: now supports (preview)")
        cleaned = [k.lower() for k in keywords]
        assert "aks" in cleaned
        assert "supports" in cleaned
        assert "preview" in cleaned
        # No trailing colons or parens
        for kw in keywords:
            assert not kw.startswith("(")
            assert not kw.endswith(")")
            assert not kw.endswith(":")

    def test_min_length_three(self):
        keywords = extract_keywords("GA of AKS v2 API release")
        lower_kws = [k.lower() for k in keywords]
        assert "ga" not in lower_kws  # length 2
        assert "v2" not in lower_kws  # length 2
        assert "aks" in lower_kws
        assert "api" in lower_kws
        assert "release" in lower_kws

    def test_removes_duplicates(self):
        keywords = extract_keywords("AKS AKS aks AKS")
        assert len(keywords) == 1

    def test_preserves_order(self):
        keywords = extract_keywords("Zebra Alpha Kilo")
        assert keywords == ["Zebra", "Alpha", "Kilo"]

    def test_empty_title(self):
        assert extract_keywords("") == []

    def test_all_stopwords(self):
        assert extract_keywords("the is a an for to") == []

    def test_all_short_words(self):
        assert extract_keywords("GA of v2 on it") == []
