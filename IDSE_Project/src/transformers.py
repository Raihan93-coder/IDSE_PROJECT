"""Reusable scikit-learn transformers for the ECG pipeline."""
from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class FixedFeatureSelector(BaseEstimator, TransformerMixin):
    """Select a fixed set of columns chosen during training-only comparison."""

    def __init__(self, indices: list[int] | None = None) -> None:
        self.indices = indices

    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> "FixedFeatureSelector":
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return X[:, self.indices]
