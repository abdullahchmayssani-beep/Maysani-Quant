"""Mean-reversion features.

This is a falsification control (Section 21.6). Nothing here asserts that
EUR/USD mean reverts profitably.
"""
from __future__ import annotations

import math
from typing import Sequence


def rolling_zscore(values: Sequence[float], window: int) -> float:
    """Z-score of the latest value against the trailing window that precedes it."""
    if len(values) < window + 1:
        raise ValueError(f"zscore needs {window + 1} values, got {len(values)}")
    reference = values[-(window + 1) : -1]
    mean = sum(reference) / window
    var = sum((v - mean) ** 2 for v in reference) / (window - 1)
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (values[-1] - mean) / sd


def distance_from_mean(values: Sequence[float], window: int) -> float:
    if len(values) < window + 1:
        raise ValueError(f"needs {window + 1} values, got {len(values)}")
    reference = values[-(window + 1) : -1]
    mean = sum(reference) / window
    return values[-1] - mean
