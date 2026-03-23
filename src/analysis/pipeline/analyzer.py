"""Step 3: LLM analysis of update content."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def analyze_update(update_id: str, content: dict, context: dict) -> dict:
    """Run LLM analysis on the scraped content and research context.

    Returns structured analysis results.
    """
    logger.info("Analyzing update %s", update_id)
    # TODO: implement LLM analysis
    raise NotImplementedError("Analyzer not yet implemented")
