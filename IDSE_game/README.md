# Touchline Data

An offline football match simulator for learning introductory data science. All clubs, players and match records are fictional and generated locally. The first playable career level teaches data cleaning, then presents an inspectable fixed model forecast and a 90-second match simulation.

## Run

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Run the command from this directory. The game stores its career balance in `data/career.json`. It does not connect to the internet or train models.
The game opens full-screen; press `F11` to switch to a resizable window.

## Controls

- Mouse: select menu items, challenge answers, teams and stake.
- `1`–`3`: choose a cleaning answer.
- `Enter` or `Space`: continue.
- `Esc`: return to the main menu.
- `F11`: toggle full-screen and windowed modes. During a match, `Esc` returns to windowed mode.

Only Level 1 (Cleaning) is playable in this first development phase. The career screen shows the remaining planned levels.
