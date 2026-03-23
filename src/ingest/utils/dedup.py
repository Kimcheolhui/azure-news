"""Deduplication logic for ingested updates."""


def is_duplicate(source_url: str, existing_urls: set[str]) -> bool:
    """Check if a URL has already been ingested."""
    return source_url in existing_urls
