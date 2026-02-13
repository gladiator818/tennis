from pathlib import Path

from tennis_analytics.data_sources.base import BaseDataSource


class CommercialApiSource(BaseDataSource):
    """Placeholder interface for paid APIs (Sportradar, Tennis Abstract premium, etc.)."""

    def __init__(self, api_key: str | None = None, provider: str = "not_configured") -> None:
        self.api_key = api_key
        self.provider = provider

    def fetch_matches(self, years: list[int], raw_dir: Path) -> list[Path]:
        raise NotImplementedError(
            "Commercial API source is a placeholder. Implement provider-specific client to fetch match stats."
        )

    def fetch_rankings(self, years: list[int], raw_dir: Path) -> list[Path]:
        raise NotImplementedError(
            "Commercial API source is a placeholder. Implement provider-specific rankings endpoint."
        )
