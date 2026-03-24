"""Seed default sources into the database."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from .models import Source

logger = logging.getLogger(__name__)

DEFAULT_SOURCES = [
    {
        "name": "azure-updates-rss",
        "display_name": "Azure Updates",
        "url": "https://www.microsoft.com/releasecommunications/api/v2/azure/rss",
        "source_type": "rss",
    },
    {
        "name": "azure-blog",
        "display_name": "Azure Official Blog",
        "url": "https://azure.microsoft.com/en-us/blog/",
        "source_type": "web",
    },
    {
        "name": "microsoft-tech-community",
        "display_name": "Tech Community",
        "url": "https://techcommunity.microsoft.com/",
        "source_type": "web",
    },
    {
        "name": "microsoft-blog",
        "display_name": "Microsoft Blog",
        "url": "https://blogs.microsoft.com/",
        "source_type": "web",
    },
    {
        "name": "fabric-blog",
        "display_name": "Fabric Blog",
        "url": "https://blog.fabric.microsoft.com/",
        "source_type": "web",
    },
    {
        "name": "github-blog",
        "display_name": "GitHub Blog",
        "url": "https://github.blog/",
        "source_type": "web",
    },
]


def seed_sources(session: Session) -> int:
    """Insert default sources if they don't already exist.
    Updates display_name for existing sources if not set.

    Returns the number of new sources created.
    """
    created = 0
    for src in DEFAULT_SOURCES:
        exists = session.query(Source).filter_by(name=src["name"]).first()
        if exists:
            if not exists.display_name and src.get("display_name"):
                exists.display_name = src["display_name"]
                logger.info("Updated display_name for source: %s", src["name"])
            logger.debug("Source %r already exists, skipping", src["name"])
            continue

        source = Source(
            id=uuid.uuid4(),
            name=src["name"],
            display_name=src.get("display_name"),
            url=src["url"],
            source_type=src["source_type"],
            enabled=src.get("enabled", True),
        )
        session.add(source)
        created += 1
        logger.info("Seeded source: %s", src["name"])

    session.flush()
    return created
