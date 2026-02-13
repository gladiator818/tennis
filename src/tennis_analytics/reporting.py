from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from tennis_analytics.config import AppConfig
from tennis_analytics.insights.engine import build_player_insights


def export_player_report(player_df: pd.DataFrame, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = build_player_insights(player_df)
    slug = payload["player_name"].lower().replace(" ", "_")

    json_path = output_dir / f"{slug}.json"
    md_path = output_dir / f"{slug}.md"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    md_lines = [
        f"# {payload['player_name']} - Coach Report",
        "",
        f"- Profile: **{payload['profile']}**",
        f"- Metrics mode: **{payload['metric_mode']}** (full vs proxy)",
        "",
        "## Strengths",
    ]
    md_lines += [f"- {s}" for s in payload["strengths"]]
    md_lines += ["", "## Weaknesses"]
    md_lines += [f"- {w}" for w in payload["weaknesses"]]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return payload


def export_top100_summary(features: pd.DataFrame, cfg: AppConfig) -> Path:
    summary = (
        features.sort_values("matches", ascending=False)
        .groupby(["player_id", "player_name"], as_index=False)
        .head(1)
        .head(100)
        [["player_id", "player_name", "surface", "tier", "matches", "win_pct", "spw_pct", "rpw_pct", "metric_mode"]]
    )
    path = cfg.reports_dir / "top100_summary.csv"
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(path, index=False)
    return path


def coverage_report(features: pd.DataFrame, cfg: AppConfig) -> Path:
    cov = features[["player_id", "player_name", "tier", "surface", "matches", "coverage_full_stats_pct", "metric_mode"]].copy()
    unavailable = [
        "hold_pct (requires service games by player)",
        "break_pct (requires return games by player)",
        "shot-level pressure metrics (requires point-level feed)",
    ]
    report_path = cfg.reports_dir / "coverage_report.md"
    lines = ["# Coverage Report", "", "## Full stats coverage by player/tier", ""]
    lines.append(cov.to_markdown(index=False))
    lines += ["", "## Missing metrics and how to obtain", ""]
    for m in unavailable:
        lines.append(f"- {m} -> fill using commercial API adapter in `CommercialApiSource`.")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
