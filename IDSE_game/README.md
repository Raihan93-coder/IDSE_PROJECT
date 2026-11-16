# IDSE Football Betting Simulator

An offline, fictional-football learning game built with Python, Pygame and pygame_gui. Uses pygame-ce, a drop-in replacement that keeps the `import pygame` API and provides wheels for current Python versions. pygame_gui 0.6.14 and later supports pygame-ce. Each round introduces a synthetic dataset and guides the player through cleaning, EDA, descriptive statistics, chart selection and a frozen prematch prediction before opening betting. Progress is stored as readable JSON in `~/.idse_football_simulator.json`.

## Run

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

The match runs for 90 seconds. During play, choose **Simulate match** to fast-forward to full time. All clubs, match records and results are fictional and generated locally. No model training or network access is needed.

## Modules

- `idse_game/world.py`: fictional fixtures and synthetic match data
- `idse_game/learning.py`: preprocessing, descriptive statistics and instant prediction
- `idse_game/betting.py`: wager odds and settlement
- `idse_game/save_system.py`: local JSON persistence
- `idse_game/app.py`: pygame_gui screens and round flow
