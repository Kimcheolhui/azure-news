"""Step 2: Find related updates and documentation."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def find_related_context(update_id: str) -> dict:
    """Find related updates and external documentation for context.

    Returns a dict with related updates and reference material.
    """
    logger.info("Researching context for update %s", update_id)
    # TODO: implement research step
    raise NotImplementedError("Researcher not yet implemented")
