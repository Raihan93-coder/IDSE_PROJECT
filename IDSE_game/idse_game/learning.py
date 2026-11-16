"""Short data-science activities and descriptive statistics."""
from __future__ import annotations
from collections import Counter
from math import sqrt
from statistics import mean, median


def clean_rows(rows: list[dict[str, object]], fill_value: float = 80.0) -> tuple[list[dict[str, object]], int, int]:
    """Remove exact duplicate rows and fill missing numeric values with a column mean."""
    unique = list({tuple(sorted(row.items())): dict(row) for row in rows}.values())
    filled = 0
    for key in ("possession", "shots", "shots_on_target", "goals", "pass_accuracy", "fouls", "corners", "yellow_cards", "xg", "rating"):
        values = [float(r[key]) for r in unique if r.get(key) is not None]
        replacement = sum(values) / len(values) if values else fill_value
        for row in unique:
            if row.get(key) is None:
                row[key] = round(replacement, 2); filled += 1
    # Cap implausible goals rather than deleting a potentially useful match.
    for row in unique:
        row["goals"] = min(int(row["goals"]), 5)
    return unique, len(rows) - len(unique), filled


def summary(values: list[float]) -> dict[str, float]:
    """Return mean, median, mode, variance, standard deviation, range and IQR."""
    ordered = sorted(values)
    q1, q3 = ordered[len(ordered)//4], ordered[(3*len(ordered))//4]
    counts = Counter(values); max_count = max(counts.values())
    return {"mean": mean(values), "median": median(values), "mode": min(v for v,c in counts.items() if c == max_count),
        "variance": sum((x-mean(values))**2 for x in values)/len(values),
        "std_dev": sqrt(sum((x-mean(values))**2 for x in values)/len(values)),
        "range": max(values)-min(values), "iqr": q3-q1}


def predict_home_win(rows: list[dict[str, object]], home_strength: float, away_strength: float, clean_quality: float = 1.0) -> float:
    """Fast precomputed-style probability heuristic; no model training occurs in play."""
    possession = sum(float(r["possession"]) for r in rows)/max(1, len(rows))
    shots = sum(float(r["shots"]) for r in rows)/max(1, len(rows))
    signal = (home_strength-away_strength)*2.0 + (possession-50)/35 + (shots-8)/18
    return max(.08, min(.82, (1/(1+pow(2.71828, -signal))) * (.65 + .35*clean_quality)))
