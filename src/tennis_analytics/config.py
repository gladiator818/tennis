from pathlib import Path

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    raw_data_dir: Path = Field(default=Path("data/raw"))
    processed_data_dir: Path = Field(default=Path("data/processed"))
    db_path: Path = Field(default=Path("db/tennis.duckdb"))
    reports_dir: Path = Field(default=Path("reports"))
    default_years: list[int] = Field(default_factory=lambda: [2023, 2024, 2025])
    commercial_api_enabled: bool = False
