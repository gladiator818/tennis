from __future__ import annotations

import pandas as pd

from tennis_analytics.features import METRICS

METRIC_LABELS = {
    "win_pct": "Win rate",
    "spw_pct": "Serve points won",
    "rpw_pct": "Return points won",
    "bp_saved_pct": "Break points saved",
    "bp_converted_pct": "Break points converted",
    "tb_win_pct": "Tiebreak win rate",
    "deciding_set_win_pct": "Deciding set win rate",
}


def _profile(row: pd.Series) -> str:
    if row.get("spw_pct_pctile", 0) >= 0.75 and row.get("rpw_pct_pctile", 0) < 0.45:
        return "serve-bot"
    if row.get("rpw_pct_pctile", 0) >= 0.7 and row.get("spw_pct_pctile", 0) < 0.6:
        return "counterpuncher"
    if row.get("spw_pct_pctile", 0) >= 0.65 and row.get("rpw_pct_pctile", 0) >= 0.65:
        return "all-court"
    return "baseliner"


def build_player_insights(player_slice: pd.DataFrame, min_items: int = 6, max_items: int = 10) -> dict:
    strengths: list[str] = []
    weaknesses: list[str] = []
    summary = player_slice.sort_values("matches", ascending=False).head(1).iloc[0]
    mode = summary["metric_mode"]

    for _, row in player_slice.iterrows():
        for metric in METRICS:
            pctile = row.get(f"{metric}_pctile")
            value = row.get(metric)
            if pd.isna(pctile) or pd.isna(value):
                continue
            evidence = f"{METRIC_LABELS[metric]}={value:.1%} ({row['surface']}, {row['tier']}, pctl={pctile:.0%})"
            if pctile >= 0.75 and len(strengths) < max_items:
                strengths.append(evidence)
            elif pctile <= 0.25 and len(weaknesses) < max_items:
                weaknesses.append(evidence)

    strengths = strengths[:max_items]
    weaknesses = weaknesses[:max_items]
    if len(strengths) < min_items:
        strengths += ["Insufficient high-percentile metrics; review matchup-specific trends."] * (min_items - len(strengths))
    if len(weaknesses) < min_items:
        weaknesses += ["No clear low-percentile weakness in this segment; monitor volatility."] * (min_items - len(weaknesses))

    return {
        "player_id": int(summary["player_id"]),
        "player_name": summary["player_name"],
        "profile": _profile(summary),
        "metric_mode": mode,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }
