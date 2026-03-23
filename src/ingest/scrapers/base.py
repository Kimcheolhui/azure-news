from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Abstract base for all source scrapers."""

    @abstractmethod
    def scrape(self) -> list[dict]:
        """Fetch and parse updates from the source. Returns list of dicts ready for Update model."""
        ...

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Identifier matching sources.name in DB."""
        ...
