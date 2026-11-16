"""Fixed offline forecast coefficients for the fictional league."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Forecast:
    """Inspectable home-win estimate and its simple feature contributions."""

    home_probability: float
    home_form: float
    away_form: float
    home_shot_rate: float


def forecast() -> Forecast:
    """Apply fixed, preconfigured weights; no fitting or network access occurs."""
    home_form, away_form, home_shot_rate = 0.67, 0.49, 0.58
    logit = -0.45 + 1.45 * home_form - 1.1 * away_form + 0.8 * home_shot_rate
    probability = 1 / (1 + 2.718281828 ** (-logit))
    return Forecast(probability, home_form, away_form, home_shot_rate)
