from abc import ABC, abstractmethod
from pathlib import Path


class BaseDataSource(ABC):
    @abstractmethod
    def fetch_matches(self, years: list[int], raw_dir: Path) -> list[Path]:
        raise NotImplementedError

    @abstractmethod
    def fetch_rankings(self, years: list[int], raw_dir: Path) -> list[Path]:
        raise NotImplementedError
