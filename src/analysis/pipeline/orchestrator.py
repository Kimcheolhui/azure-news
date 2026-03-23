"""Sequential pipeline runner for report generation."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def run_pipeline(update_id: str) -> None:
    """Run the full analysis pipeline for a single update.

    Steps:
        1. deep_scraper  – fetch full article content
        2. researcher    – find related updates and docs
        3. analyzer      – LLM analysis of the content
        4. writer        – LLM report generation
    """
    logger.info("Pipeline started for update %s", update_id)
    # TODO: implement pipeline orchestration
    raise NotImplementedError("Pipeline orchestration not yet implemented")
