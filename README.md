# IDSE Course Project

Course projects for Introduction to Data Science for Engineers (IDSE).

## Group Members

- Raihan
- Sinan
- Jyothis

## Projects

### ECG Arrhythmia Classification — `ML_Project/`

An end-to-end ECG heartbeat classification project using a Random Forest classifier. It prepares the dataset, performs exploratory analysis and evaluation, and generates project reports. The dataset is downloaded on the first run.

Run from `ML_Project/`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/train.py
```

### Touchline Data — `IDSE_game/`

An offline Pygame football simulator for practicing introductory data science. The current playable level covers data cleaning, followed by a fixed-model forecast and a 90-second fictional match.

Run from `IDSE_game/`:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

See each project's README for details and controls: [ECG classifier](ML_Project/README.md) · [Touchline Data](IDSE_game/README.md).
