"""Step 4: LLM report generation."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def write_report(update_id: str, analysis: dict) -> dict:
    """Generate the final report using LLM based on analysis results.

    Returns the report content in Korean and English.
    """
    logger.info("Writing report for update %s", update_id)
    # TODO: implement LLM report writing
    raise NotImplementedError("Writer not yet implemented")
