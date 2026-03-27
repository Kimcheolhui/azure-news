"""Scraper for the Microsoft Fabric Blog."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

import feedparser
from bs4 import BeautifulSoup

from .base import BaseScraper
from ..utils.parsing import parse_datetime, strip_html

logger = logging.getLogger(__name__)

BLOG_URL = "https://blog.fabric.microsoft.com/"
COMMON_FEED_PATHS = ["/feed/", "/rss/", "/blog/feed/"]
REQUEST_TIMEOUT = 30


class FabricBlogScraper(BaseScraper):
    """Fetch and parse Microsoft Fabric Blog posts.

    Strategy:
    1. Try RSS feed first (most reliable), paginating with ``?paged=N``.
    2. Fall back to scraping HTML listing pages, following next-page links.
    """

    @property
    def source_name(self) -> str:
        return "fabric-blog"

    def scrape(self) -> list[dict]:
        results = self._try_rss()
        if results:
            return results

        logger.info("RSS feed empty or unavailable, falling back to HTML scrape")
        return self._try_html()

    # ------------------------------------------------------------------
    # RSS path (with pagination)
    # ------------------------------------------------------------------

    def _try_rss(self) -> list[dict]:
        feed_url = self._discover_feed_url()
        if not feed_url:
            feed_url = self._probe_common_feed_paths()

        if not feed_url:
            logger.warning("No RSS feed found for Fabric Blog")
            return []

        all_results: list[dict] = []
        seen_urls: set[str] = set()

        for page in range(1, self._max_pages + 1):
            paged_url = feed_url if page == 1 else f"{feed_url}?paged={page}"
            logger.info("Trying Fabric Blog RSS feed page %d: %s", page, paged_url)

            try:
                resp = self._http.get(paged_url)
                resp.raise_for_status()
            except Exception as exc:
                if page == 1:
                    logger.warning("Could not fetch blog RSS feed: %s", exc)
                else:
                    logger.debug("RSS page %d unavailable (end of feed): %s", page, exc)
                break

            feed = feedparser.parse(resp.text)
            if feed.bozo and not feed.entries:
                if page == 1:
                    logger.warning("feedparser error on blog feed: %s", feed.bozo_exception)
                break

            if not feed.entries:
                logger.debug("RSS page %d returned 0 entries, stopping", page)
                break

            page_results = self._parse_feed_entries(feed.entries, seen_urls)
            if not page_results:
                logger.debug("RSS page %d had no new entries, stopping", page)
                break

            all_results.extend(page_results)

        logger.info("Parsed %d total entries from Fabric Blog RSS", len(all_results))
        return all_results

    def _parse_feed_entries(
        self, entries: list, seen_urls: set[str]
    ) -> list[dict]:
        """Parse feed entries, skipping URLs already seen across pages."""
        results: list[dict] = []
        for entry in entries:
            url = entry.get("link", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)

            published = self._parse_published(entry)
            categories = [t.term for t in getattr(entry, "tags", []) if hasattr(t, "term")]

            results.append(
                {
                    "title": entry.get("title", ""),
                    "source_url": url,
                    "published_date": published,
                    "summary": strip_html(entry.get("summary", "")),
                    "categories": categories or None,
                    "raw_data": dict(entry),
                }
            )
        return results

    def _discover_feed_url(self) -> str | None:
        """Look for an RSS <link> tag in the blog HTML head."""
        try:
            resp = self._http.get(BLOG_URL)
            resp.raise_for_status()
        except Exception:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        link = soup.find("link", attrs={"type": "application/rss+xml"})
        if link and link.get("href"):
            href = link["href"]
            if href.startswith("/"):
                href = urljoin(BLOG_URL, href)
            logger.info("Discovered blog RSS feed URL: %s", href)
            return href
        return None

    def _probe_common_feed_paths(self) -> str | None:
        """Try common feed paths and return the first that responds with valid XML."""
        for path in COMMON_FEED_PATHS:
            url = urljoin(BLOG_URL, path)
            try:
                resp = self._http.get(url)
                if resp.ok and ("xml" in resp.headers.get("content-type", "") or "<rss" in resp.text[:500]):
                    logger.info("Found feed at common path: %s", url)
                    return url
            except Exception:
                continue
        return None

    # ------------------------------------------------------------------
    # HTML scrape fallback (with pagination)
    # ------------------------------------------------------------------

    def _try_html(self) -> list[dict]:
        all_results: list[dict] = []
        seen_urls: set[str] = set()
        page_url: str | None = BLOG_URL

        for page in range(1, self._max_pages + 1):
            if not page_url:
                break

            logger.info("Scraping Fabric Blog HTML page %d: %s", page, page_url)
            try:
                resp = self._http.get(page_url)
                resp.raise_for_status()
            except Exception as exc:
                logger.error("Failed to fetch blog page: %s", exc)
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            page_results = self._parse_html_articles(soup, seen_urls)

            if not page_results:
                logger.debug("HTML page %d had no new articles, stopping", page)
                break

            all_results.extend(page_results)
            page_url = self._find_next_page_url(soup)

        logger.info("Parsed %d total entries from Fabric Blog HTML", len(all_results))
        return all_results

    def _parse_html_articles(
        self, soup: BeautifulSoup, seen_urls: set[str]
    ) -> list[dict]:
        """Extract articles from a single HTML page."""
        results: list[dict] = []

        articles = (
            soup.select("article")
            or soup.select(".post-item")
            or soup.select("[data-bi-area='blog-post']")
            or soup.select(".card")
        )

        for article in articles:
            title_tag = article.find(["h2", "h3", "h4"]) or article.find("a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link_tag = title_tag if title_tag.name == "a" else title_tag.find("a")
            href = link_tag["href"] if link_tag and link_tag.get("href") else ""
            if href and href.startswith("/"):
                href = urljoin(BLOG_URL, href)

            if not href or href in seen_urls:
                continue
            seen_urls.add(href)

            time_tag = article.find("time")
            published = None
            if time_tag:
                published = parse_datetime(
                    time_tag.get("datetime") or time_tag.get_text(strip=True)
                )

            summary_tag = article.find("p")
            summary = summary_tag.get_text(strip=True) if summary_tag else ""

            results.append(
                {
                    "title": title,
                    "source_url": href,
                    "published_date": published,
                    "summary": summary,
                    "categories": None,
                    "raw_data": {"html_snippet": str(article)[:2000]},
                }
            )

        return results

    def _find_next_page_url(self, soup: BeautifulSoup) -> str | None:
        """Find the next-page link from pagination elements."""
        next_link = soup.find("a", attrs={"rel": "next"})
        if next_link and next_link.get("href"):
            return urljoin(BLOG_URL, next_link["href"])

        for selector in ("a.next", "a.page-numbers.next", ".pagination a.next"):
            tag = soup.select_one(selector)
            if tag and tag.get("href"):
                return urljoin(BLOG_URL, tag["href"])

        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_published(entry) -> datetime | None:
        for field in ("published", "updated"):
            val = entry.get(field)
            if val:
                dt = parse_datetime(val)
                if dt is not None:
                    return dt
        for field in ("published_parsed", "updated_parsed"):
            st = entry.get(field)
            if st:
                try:
                    return datetime(*st[:6], tzinfo=timezone.utc)
                except Exception:
                    pass
        return None
