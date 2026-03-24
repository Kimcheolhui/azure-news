"""Tests for analysis.utils.content_parser."""

from analysis.utils.content_parser import html_to_text, truncate_for_llm


class TestHtmlToText:
    def test_basic_html(self):
        html = "<p>Hello <b>world</b></p>"
        result = html_to_text(html)
        assert "Hello" in result
        assert "world" in result

    def test_removes_scripts(self):
        html = "<p>Content</p><script>alert('xss')</script>"
        result = html_to_text(html)
        assert "alert" not in result
        assert "Content" in result

    def test_removes_styles(self):
        html = "<p>Visible</p><style>body{color:red}</style>"
        result = html_to_text(html)
        assert "color" not in result
        assert "Visible" in result

    def test_removes_nav_header_footer_aside(self):
        html = (
            "<nav>Menu</nav>"
            "<header>Header</header>"
            "<main><p>Main content</p></main>"
            "<footer>Footer</footer>"
            "<aside>Sidebar</aside>"
        )
        result = html_to_text(html)
        assert "Menu" not in result
        assert "Header" not in result
        assert "Footer" not in result
        assert "Sidebar" not in result
        assert "Main content" in result

    def test_collapses_blank_lines(self):
        html = "<p>Line 1</p><br><br><br><p>Line 2</p>"
        result = html_to_text(html)
        lines = result.splitlines()
        assert all(line.strip() for line in lines)

    def test_empty_html(self):
        assert html_to_text("") == ""

    def test_plain_text_passthrough(self):
        text = "Just plain text"
        assert html_to_text(text) == text


class TestTruncateForLlm:
    def test_short_text_unchanged(self):
        text = "Short text"
        assert truncate_for_llm(text) == text

    def test_exact_limit_unchanged(self):
        text = "x" * 15000
        assert truncate_for_llm(text) == text

    def test_over_limit_truncated(self):
        text = "x" * 20000
        result = truncate_for_llm(text)
        assert result.endswith("[Content truncated]")
        assert len(result) < 20000

    def test_custom_limit(self):
        text = "Hello world, this is a test."
        result = truncate_for_llm(text, max_chars=10)
        assert result.startswith("Hello worl")
        assert "[Content truncated]" in result

    def test_truncation_preserves_prefix(self):
        text = "ABCDE" * 5000
        result = truncate_for_llm(text, max_chars=100)
        assert result.startswith("ABCDE" * 20)
