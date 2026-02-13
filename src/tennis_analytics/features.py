from __future__ import annotations

import duckdb
import numpy as np
import pandas as pd

from tennis_analytics.config import AppConfig


METRICS = [
    "win_pct",
    "spw_pct",
    "rpw_pct",
    "bp_saved_pct",
    "bp_converted_pct",
    "tb_win_pct",
    "deciding_set_win_pct",
]


def _safe_div(n: pd.Series, d: pd.Series) -> pd.Series:
    return np.where(d > 0, n / d, np.nan)


def compute_player_features(cfg: AppConfig, period: str = "52w") -> pd.DataFrame:
    con = duckdb.connect(str(cfg.db_path))
    df = con.execute("SELECT * FROM match_stats").df()
    con.close()

    df["date"] = pd.to_datetime(df["date"])
    max_date = df["date"].max()
    if period == "52w":
        df = df[df["date"] >= max_date - pd.Timedelta(days=364)]

    df["vs_top10"] = df["opponent_rank"].fillna(9999) <= 10
    df["vs_top20"] = df["opponent_rank"].fillna(9999) <= 20

    group_cols = ["player_id", "player_name", "surface", "tier"]
    agg = (
        df.groupby(group_cols, dropna=False)
        .agg(
            matches=("match_id", "count"),
            wins=("won", "sum"),
            spw=("spw", "sum"),
            svpt=("svpt", "sum"),
            rpw=("rpw", "sum"),
            rpt=("rpt", "sum"),
            bp_saved=("bp_saved", "sum"),
            bp_faced=("bp_faced", "sum"),
            bp_won_return=("bp_won_return", "sum"),
            bp_chances_return=("bp_chances_return", "sum"),
            tb_played=("tb_played", "sum"),
            tb_won=("tb_won", "sum"),
            deciding_set_played=("deciding_set", "sum"),
            deciding_set_won=("deciding_set_won", "sum"),
            full_stats_matches=("has_full_stats", "sum"),
            vs_top10_wins=("vs_top10", lambda s: int(df.loc[s.index, "won"][s].sum())),
            vs_top10_matches=("vs_top10", "sum"),
            vs_top20_wins=("vs_top20", lambda s: int(df.loc[s.index, "won"][s].sum())),
            vs_top20_matches=("vs_top20", "sum"),
        )
        .reset_index()
    )

    agg["win_pct"] = _safe_div(agg["wins"], agg["matches"])
    agg["spw_pct"] = _safe_div(agg["spw"], agg["svpt"])
    agg["rpw_pct"] = _safe_div(agg["rpw"], agg["rpt"])
    agg["bp_saved_pct"] = _safe_div(agg["bp_saved"], agg["bp_faced"])
    agg["bp_converted_pct"] = _safe_div(agg["bp_won_return"], agg["bp_chances_return"])
    agg["tb_win_pct"] = _safe_div(agg["tb_won"], agg["tb_played"])
    agg["deciding_set_win_pct"] = _safe_div(agg["deciding_set_won"], agg["deciding_set_played"])
    agg["vs_top10_win_pct"] = _safe_div(agg["vs_top10_wins"], agg["vs_top10_matches"])
    agg["vs_top20_win_pct"] = _safe_div(agg["vs_top20_wins"], agg["vs_top20_matches"])
    agg["coverage_full_stats_pct"] = _safe_div(agg["full_stats_matches"], agg["matches"])

    for metric in METRICS:
        agg[f"{metric}_pctile"] = agg.groupby("surface")[metric].rank(pct=True)
        agg[f"{metric}_z"] = agg.groupby("surface")[metric].transform(lambda s: (s - s.mean()) / (s.std(ddof=0) + 1e-9))

    agg["metric_mode"] = np.where(agg["coverage_full_stats_pct"] >= 0.7, "full", "proxy")
    return agg
