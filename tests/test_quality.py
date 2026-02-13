import pandas as pd

from tennis_analytics.quality import run_quality_checks


def test_quality_checks_detect_duplicates_and_missing():
    df = pd.DataFrame(
        {
            "match_id": ["1", "1"],
            "player_id": [10, None],
            "won": [1, 0],
            "tb_won": [1, 0],
            "tb_played": [1, 1],
            "deciding_set_won": [0, 0],
            "deciding_set": [0, 0],
            "svpt": [50, 40],
            "rpt": [45, 42],
        }
    )
    issues = run_quality_checks(df)
    assert "missing_player_id" in issues
    assert "duplicate_match_player_rows" in issues
