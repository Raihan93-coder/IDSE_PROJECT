"""Human-readable local save data."""
from __future__ import annotations
import json
from pathlib import Path

SAVE_PATH = Path.home() / ".idse_football_simulator.json"
DEFAULT = {"money": 10000, "round": 1, "unlocks": ["Cleaning"], "wins": 0, "losses": 0, "settings": {"volume": 0.6}}

def load(path: Path = SAVE_PATH) -> dict:
    """Load progress, returning a fresh save when none exists or it is invalid."""
    try:
        data = json.loads(path.read_text(encoding="utf-8")); return {**DEFAULT, **data}
    except (OSError, ValueError, TypeError):
        return dict(DEFAULT)

def save(data: dict, path: Path = SAVE_PATH) -> None:
    """Write progress as readable, indented JSON."""
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, indent=2), encoding="utf-8")
