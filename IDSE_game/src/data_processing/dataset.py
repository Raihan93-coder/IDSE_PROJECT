"""Create a small, reproducible dataset with common data quality problems."""

from __future__ import annotations

import random


CLUBS = ("Harbor FC", "Cedar Town", "Metro Athletic", "Dune Rovers", "Bluepeak United")


def generate_history(seed: int = 17, rows: int = 12) -> list[dict[str, object]]:
    """Return fake historical match records with missing, duplicate and invalid data."""
    rng = random.Random(seed)
    records = [
        {"club": rng.choice(CLUBS), "shots": rng.randint(3, 17), "goals": rng.randint(0, 4)}
        for _ in range(rows)
    ]
    records[2]["shots"] = None
    records[5]["club"] = "  harbor fc "
    records[8]["goals"] = -3
    records[10] = dict(records[1])
    return records


def clean_history(records: list[dict[str, object]]) -> list[dict[str, object]]:
    """Normalize labels, fill missing shots with the median, and remove invalid rows."""
    shots = sorted(int(row["shots"]) for row in records if isinstance(row.get("shots"), int))
    median_shots = shots[len(shots) // 2]
    cleaned: list[dict[str, object]] = []
    seen: set[tuple[object, ...]] = set()
    for original in records:
        if not isinstance(original.get("goals"), int) or int(original["goals"]) < 0:
            continue
        row = dict(original)
        row["club"] = str(row["club"]).strip().title()
        row["shots"] = int(row["shots"]) if isinstance(row["shots"], int) else median_shots
        signature = (row["club"], row["shots"], row["goals"])
        if signature not in seen:
            seen.add(signature)
            cleaned.append(row)
    return cleaned


def sample_rows() -> list[dict[str, object]]:
    """Return a stable subset shown in the cleaning challenge."""
    return generate_history()[:6]
