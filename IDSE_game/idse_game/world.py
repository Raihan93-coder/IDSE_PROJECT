"""Deterministic fictional football world and learning datasets."""
from __future__ import annotations
from dataclasses import dataclass
import random

TEAM_NAMES = ("Coppervale Rovers", "Mistral Athletic", "Juniper City", "Northstar FC", "Emberford United", "Silverfen Town", "Cinderport SC", "Verdant Vale")
PLAYER_NAMES = ("Ari Sol", "Mina Vale", "Tavi Noor", "Kiran Moss", "Niko Reed", "Sana Pike", "Eli Rowan", "Zoya Finch")
STADIUMS = ("Lantern Park", "The Glass Bowl", "Mossbank Ground", "Copperfield Arena", "Northwind Stadium", "Riverstone Park")

@dataclass(frozen=True)
class Match:
    home: str
    away: str
    stadium: str
    home_strength: float
    away_strength: float
    round_number: int


def make_match(round_number: int, rng: random.Random | None = None) -> Match:
    """Create a fictional, reproducible match for the given round."""
    rng = rng or random.Random(round_number * 917)
    home, away = rng.sample(TEAM_NAMES, 2)
    return Match(home, away, rng.choice(STADIUMS), rng.uniform(.35, .85), rng.uniform(.35, .85), round_number)


def make_dataset(match: Match, seed: int | None = None) -> list[dict[str, object]]:
    """Build a small synthetic historical-match dataset with teachable data issues."""
    rng = random.Random(seed if seed is not None else match.round_number * 541)
    rows = []
    for i in range(18):
        possession = rng.randint(32, 68)
        shots = max(1, round(rng.gauss(8 + (possession - 50) / 5, 3)))
        rows.append({"match_id": f"M{i+1:02}", "team": match.home if i % 2 == 0 else match.away,
            "possession": possession, "shots": shots, "shots_on_target": min(shots, rng.randint(1, max(1, shots))),
            "goals": min(5, rng.choices([0, 1, 2, 3], [35, 38, 21, 6])[0]),
            "pass_accuracy": rng.randint(65, 96), "fouls": rng.randint(4, 19),
            "corners": rng.randint(0, 12), "yellow_cards": rng.randint(0, 5),
            "xg": round(rng.uniform(.1, 3.2), 2), "rating": round(rng.uniform(5.2, 9.7), 1)})
    # Intentional issues are fixed in the cleaning activity.
    rows[2]["pass_accuracy"] = None
    rows[7]["xg"] = None
    rows.append(dict(rows[3]))
    rows[14]["goals"] = 9  # synthetic outlier
    return rows
