"""Step 1: Full content scraping for analysis."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def scrape_full_content(source_url: str) -> dict:
    """Scrape the full article content from the source URL.

    Returns a dict with scraped content suitable for LLM input.
    """
    logger.info("Scraping full content from %s", source_url)
    # TODO: implement deep scraping
    raise NotImplementedError("Deep scraper not yet implemented")
