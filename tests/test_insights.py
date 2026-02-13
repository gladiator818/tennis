import pandas as pd

from tennis_analytics.insights.engine import build_player_insights


def test_insights_minimum_items():
    df = pd.DataFrame(
        [
            {
                "player_id": 1,
                "player_name": "Test Player",
                "surface": "Hard",
                "tier": "ATP 500",
                "matches": 10,
                "metric_mode": "proxy",
                "win_pct": 0.8,
                "win_pct_pctile": 0.9,
                "spw_pct": 0.65,
                "spw_pct_pctile": 0.8,
                "rpw_pct": 0.3,
                "rpw_pct_pctile": 0.1,
                "bp_saved_pct": 0.7,
                "bp_saved_pct_pctile": 0.8,
                "bp_converted_pct": 0.3,
                "bp_converted_pct_pctile": 0.2,
                "tb_win_pct": 0.8,
                "tb_win_pct_pctile": 0.9,
                "deciding_set_win_pct": 0.4,
                "deciding_set_win_pct_pctile": 0.2,
            }
        ]
    )
    r = build_player_insights(df)
    assert len(r["strengths"]) >= 6
    assert len(r["weaknesses"]) >= 6
