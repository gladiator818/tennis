from __future__ import annotations

import pandas as pd


def run_quality_checks(match_stats: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    if match_stats["player_id"].isna().any():
        issues.append("missing_player_id")
    if match_stats.duplicated(subset=["match_id", "player_id"]).any():
        issues.append("duplicate_match_player_rows")
    pct_columns = ["won", "tb_won", "tb_played", "deciding_set_won", "deciding_set"]
    for col in pct_columns:
        if not match_stats[col].dropna().isin([0, 1, True, False]).all():
            issues.append(f"invalid_binary_{col}")
    if (match_stats["svpt"] < 0).any() or (match_stats["rpt"] < 0).any():
        issues.append("negative_points")
    return issues
