"""Load and save the small offline player career profile."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


SAVE_PATH = Path(__file__).resolve().parents[2] / "data" / "career.json"


@dataclass
class Profile:
    """Career balance and completed match count."""

    balance: int = 10_000
    levels_completed: int = 0
    matches_played: int = 0

    @classmethod
    def load(cls) -> "Profile":
        """Load the local profile, falling back safely to a new career."""
        try:
            values = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
            return cls(**{key: int(values.get(key, default)) for key, default in {
                "balance": 10_000, "levels_completed": 0, "matches_played": 0
            }.items()})
        except (OSError, ValueError, TypeError):
            return cls()

    def save(self) -> None:
        """Write the career profile locally without network access."""
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        SAVE_PATH.write_text(json.dumps(self.__dict__, indent=2), encoding="utf-8")
