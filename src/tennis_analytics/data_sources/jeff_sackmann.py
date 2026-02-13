from pathlib import Path
from urllib.request import urlretrieve

from tennis_analytics.data_sources.base import BaseDataSource


class JeffSackmannSource(BaseDataSource):
    """Open-source ingestion from Jeff Sackmann ATP datasets."""

    base_url = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master"

    def _download_if_missing(self, url: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            urlretrieve(url, destination)
        return destination

    def fetch_matches(self, years: list[int], raw_dir: Path) -> list[Path]:
        files: list[Path] = []
        for year in years:
            file_name = f"atp_matches_{year}.csv"
            url = f"{self.base_url}/{file_name}"
            files.append(self._download_if_missing(url, raw_dir / file_name))
        return files

    def fetch_rankings(self, years: list[int], raw_dir: Path) -> list[Path]:
        files: list[Path] = []
        for year in years:
            file_name = f"atp_rankings_{year}.csv"
            url = f"{self.base_url}/{file_name}"
            try:
                files.append(self._download_if_missing(url, raw_dir / file_name))
            except Exception:
                continue
        return files
