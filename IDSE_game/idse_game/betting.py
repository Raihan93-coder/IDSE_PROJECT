"""Simple wager settlement with capped stakes and odds."""
from __future__ import annotations

ODDS = {"Home win": 2.1, "Draw": 3.1, "Away win": 3.2, "Over 2.5 goals": 1.9, "Correct score 1-0": 7.0}

def settle(balance: int, stake: int, bet: str, home_goals: int, away_goals: int) -> tuple[int, int]:
    """Settle a bet; return updated balance and net change."""
    stake = max(0, min(int(stake), balance))
    won = {"Home win": home_goals > away_goals, "Draw": home_goals == away_goals,
           "Away win": away_goals > home_goals, "Over 2.5 goals": home_goals + away_goals >= 3,
           "Correct score 1-0": (home_goals, away_goals) == (1, 0)}.get(bet, False)
    change = round(stake * (ODDS[bet]-1)) if won else -stake
    return balance + change, change
