from __future__ import annotations

from pathlib import Path

import pandas as pd
import typer

from tennis_analytics.config import AppConfig
from tennis_analytics.data_sources.commercial_api import CommercialApiSource
from tennis_analytics.data_sources.jeff_sackmann import JeffSackmannSource
from tennis_analytics.etl import build_processed_layer, load_to_duckdb
from tennis_analytics.features import compute_player_features
from tennis_analytics.quality import run_quality_checks
from tennis_analytics.reporting import coverage_report, export_player_report, export_top100_summary

app = typer.Typer(help="ATP Top-100 performance analytics CLI")


def _get_source(source: str):
    if source == "jeff":
        return JeffSackmannSource()
    if source == "commercial":
        return CommercialApiSource()
    raise ValueError(f"Unsupported source: {source}")


@app.command()
def ingest(years: str = "2023,2024,2025", source: str = "jeff"):
    cfg = AppConfig()
    y = [int(v) for v in years.split(",")]
    ds = _get_source(source)
    match_files = ds.fetch_matches(y, cfg.raw_data_dir)
    ranking_files = ds.fetch_rankings(y, cfg.raw_data_dir)
    artifacts = build_processed_layer(match_files, ranking_files, cfg)
    load_to_duckdb(artifacts, cfg)
    df = pd.read_csv(artifacts.matches_path)
    issues = run_quality_checks(df)
    typer.echo(f"Ingestion complete. Quality issues: {issues if issues else 'none'}")


@app.command()
def report_player(player: str, period: str = "52w", out_dir: Path = Path("reports/players")):
    features = compute_player_features(AppConfig(), period=period)
    player_df = features[features["player_name"].str.lower() == player.lower()]
    if player_df.empty:
        raise typer.BadParameter(f"Player not found: {player}")
    payload = export_player_report(player_df, out_dir)
    typer.echo(f"Generated report for {payload['player_name']}")


@app.command()
def report_top100(period: str = "52w"):
    cfg = AppConfig()
    features = compute_player_features(cfg, period=period)
    path = export_top100_summary(features, cfg)
    typer.echo(f"Top-100 summary exported: {path}")


@app.command()
def report_all_players(period: str = "52w", out_dir: Path = Path("reports/players")):
    cfg = AppConfig()
    features = compute_player_features(cfg, period=period)
    top = (
        features.sort_values("matches", ascending=False)
        .groupby(["player_id", "player_name"], as_index=False)
        .head(1)
        .head(100)
    )
    for _, row in top.iterrows():
        export_player_report(features[features["player_id"] == row["player_id"]], out_dir)
    typer.echo(f"Generated {len(top)} player reports")


@app.command()
def report_coverage(period: str = "52w"):
    cfg = AppConfig()
    features = compute_player_features(cfg, period=period)
    path = coverage_report(features, cfg)
    typer.echo(f"Coverage report exported: {path}")


if __name__ == "__main__":
    app()
