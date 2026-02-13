from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd

from tennis_analytics.config import AppConfig


ATP_500_HINTS = {
    "rio de janeiro",
    "barcelona",
    "rotterdam",
    "acapulco",
    "dubai",
    "washington",
    "beijing",
    "tokyo",
    "basel",
    "vienna",
    "halle",
    "queen",
    "hamburg",
}


@dataclass
class ETLArtifacts:
    players_path: Path
    matches_path: Path
    rankings_path: Path


def _classify_tier(level: str, tourney_name: str) -> str:
    lname = (tourney_name or "").lower()
    if level == "G":
        return "Grand Slam"
    if level == "M":
        return "ATP 1000"
    if level == "A":
        return "ATP 500" if any(h in lname for h in ATP_500_HINTS) else "ATP 250"
    return "Other"


def _is_indoor(tourney_name: str) -> bool:
    name = (tourney_name or "").lower()
    return "indoor" in name or " paris" in name or "metz" in name


def _parse_score(score: str) -> tuple[int, int, bool, bool]:
    if not isinstance(score, str) or score in {"", "W/O", "RET", "DEF", "ABD"}:
        return 0, 0, False, False
    winner_sets = 0
    loser_sets = 0
    tb_played = False
    for token in score.split():
        if "-" not in token:
            continue
        clean = token.split("(")[0]
        parts = clean.split("-")
        if len(parts) != 2:
            continue
        try:
            a, b = int(parts[0]), int(parts[1])
        except ValueError:
            continue
        if a > b:
            winner_sets += 1
        else:
            loser_sets += 1
        if "(" in token:
            tb_played = True
    deciding = winner_sets + loser_sets >= 3
    return winner_sets, loser_sets, tb_played, deciding


def build_processed_layer(match_files: list[Path], ranking_files: list[Path], cfg: AppConfig) -> ETLArtifacts:
    matches_raw = pd.concat([pd.read_csv(f) for f in match_files], ignore_index=True)
    matches_raw["tourney_date"] = pd.to_datetime(matches_raw["tourney_date"].astype(str), format="%Y%m%d", errors="coerce")
    matches_raw = matches_raw.dropna(subset=["winner_id", "loser_id", "tourney_date"])

    parsed = matches_raw["score"].apply(_parse_score)
    matches_raw[["winner_sets", "loser_sets", "tb_played", "deciding_set"]] = pd.DataFrame(parsed.tolist(), index=matches_raw.index)
    matches_raw["tier"] = matches_raw.apply(lambda r: _classify_tier(r.get("tourney_level", ""), r.get("tourney_name", "")), axis=1)
    matches_raw["is_indoor"] = matches_raw["tourney_name"].apply(_is_indoor)
    matches_raw["has_full_stats"] = matches_raw[["w_svpt", "w_1stWon", "w_2ndWon", "w_bpSaved", "w_bpFaced"]].notna().all(axis=1)

    winners = pd.DataFrame(
        {
            "match_id": matches_raw.index.astype(str),
            "date": matches_raw["tourney_date"],
            "player_id": matches_raw["winner_id"].astype(int),
            "player_name": matches_raw["winner_name"],
            "opponent_id": matches_raw["loser_id"].astype(int),
            "opponent_name": matches_raw["loser_name"],
            "player_rank": matches_raw["winner_rank"],
            "opponent_rank": matches_raw["loser_rank"],
            "surface": matches_raw["surface"].fillna("Unknown"),
            "tier": matches_raw["tier"],
            "is_indoor": matches_raw["is_indoor"],
            "won": 1,
            "tb_played": matches_raw["tb_played"],
            "tb_won": matches_raw["tb_played"],
            "deciding_set": matches_raw["deciding_set"],
            "deciding_set_won": matches_raw["deciding_set"],
            "spw": (matches_raw["w_1stWon"].fillna(0) + matches_raw["w_2ndWon"].fillna(0)).astype(float),
            "svpt": matches_raw["w_svpt"].fillna(0).astype(float),
            "rpw": (matches_raw["l_svpt"].fillna(0) - matches_raw["l_1stWon"].fillna(0) - matches_raw["l_2ndWon"].fillna(0)).astype(float),
            "rpt": matches_raw["l_svpt"].fillna(0).astype(float),
            "bp_saved": matches_raw["w_bpSaved"].fillna(0).astype(float),
            "bp_faced": matches_raw["w_bpFaced"].fillna(0).astype(float),
            "bp_won_return": (matches_raw["l_bpFaced"].fillna(0) - matches_raw["l_bpSaved"].fillna(0)).astype(float),
            "bp_chances_return": matches_raw["l_bpFaced"].fillna(0).astype(float),
            "has_full_stats": matches_raw["has_full_stats"],
        }
    )

    losers = winners.copy()
    losers["player_id"] = matches_raw["loser_id"].astype(int)
    losers["player_name"] = matches_raw["loser_name"]
    losers["opponent_id"] = matches_raw["winner_id"].astype(int)
    losers["opponent_name"] = matches_raw["winner_name"]
    losers["player_rank"] = matches_raw["loser_rank"]
    losers["opponent_rank"] = matches_raw["winner_rank"]
    losers["won"] = 0
    losers["tb_won"] = 0
    losers["deciding_set_won"] = 0
    losers["spw"] = (matches_raw["l_1stWon"].fillna(0) + matches_raw["l_2ndWon"].fillna(0)).astype(float)
    losers["svpt"] = matches_raw["l_svpt"].fillna(0).astype(float)
    losers["rpw"] = (matches_raw["w_svpt"].fillna(0) - matches_raw["w_1stWon"].fillna(0) - matches_raw["w_2ndWon"].fillna(0)).astype(float)
    losers["rpt"] = matches_raw["w_svpt"].fillna(0).astype(float)
    losers["bp_saved"] = matches_raw["l_bpSaved"].fillna(0).astype(float)
    losers["bp_faced"] = matches_raw["l_bpFaced"].fillna(0).astype(float)
    losers["bp_won_return"] = (matches_raw["w_bpFaced"].fillna(0) - matches_raw["w_bpSaved"].fillna(0)).astype(float)
    losers["bp_chances_return"] = matches_raw["w_bpFaced"].fillna(0).astype(float)

    player_matches = pd.concat([winners, losers], ignore_index=True)

    players = (
        player_matches[["player_id", "player_name"]]
        .drop_duplicates(subset=["player_id"])
        .rename(columns={"player_id": "id", "player_name": "name"})
        .sort_values("name")
    )

    if ranking_files:
        rankings = pd.concat([pd.read_csv(f, names=["ranking_date", "rank", "player_id", "points"]) for f in ranking_files], ignore_index=True)
        rankings["ranking_date"] = pd.to_datetime(rankings["ranking_date"].astype(str), format="%Y%m%d", errors="coerce")
    else:
        rankings = (
            player_matches.dropna(subset=["player_rank"])
            .sort_values("date")
            .groupby("player_id", as_index=False)
            .tail(1)[["date", "player_rank", "player_id"]]
            .rename(columns={"date": "ranking_date", "player_rank": "rank"})
        )
        rankings["points"] = pd.NA

    cfg.processed_data_dir.mkdir(parents=True, exist_ok=True)
    players_path = cfg.processed_data_dir / "players.csv"
    matches_path = cfg.processed_data_dir / "match_stats.csv"
    rankings_path = cfg.processed_data_dir / "rankings.csv"
    players.to_csv(players_path, index=False)
    player_matches.to_csv(matches_path, index=False)
    rankings.to_csv(rankings_path, index=False)
    return ETLArtifacts(players_path, matches_path, rankings_path)


def load_to_duckdb(artifacts: ETLArtifacts, cfg: AppConfig) -> None:
    cfg.db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(cfg.db_path))
    con.execute("CREATE OR REPLACE TABLE players AS SELECT * FROM read_csv_auto(?)", [str(artifacts.players_path)])
    con.execute("CREATE OR REPLACE TABLE match_stats AS SELECT * FROM read_csv_auto(?)", [str(artifacts.matches_path)])
    con.execute("CREATE OR REPLACE TABLE rankings AS SELECT * FROM read_csv_auto(?)", [str(artifacts.rankings_path)])
    con.execute(
        """
        CREATE OR REPLACE TABLE matches AS
        SELECT DISTINCT match_id, date, surface, tier, is_indoor FROM match_stats
        """
    )
    con.close()
