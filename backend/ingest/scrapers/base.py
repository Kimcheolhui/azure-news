from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import requests

from ..utils.http import create_session

# Safety limit to prevent infinite pagination loops
MAX_PAGES = 10


class BaseScraper(ABC):
    """Abstract base for all source scrapers."""

    def __init__(self, max_pages: int = MAX_PAGES) -> None:
        self._http: requests.Session = create_session()
        self._max_pages = max_pages

    @abstractmethod
    def scrape(self) -> list[dict[str, Any]]:
        """Fetch and parse updates from the source. Returns list of dicts ready for Update model."""
        ...

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Identifier matching sources.name in DB."""
        ...
