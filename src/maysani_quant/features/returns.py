"""Return features. Rolling only - global normalisation is prohibited (13.3)."""
from __future__ import annotations

import math
from collections.abc import Sequence


def log_return(prev: float, current: float) -> float:
    if prev <= 0 or current <= 0:
        raise ValueError("log return requires positive prices")
    return math.log(current / prev)


def log_returns(closes: Sequence[float]) -> list[float]:
    return [log_return(closes[i - 1], closes[i]) for i in range(1, len(closes))]


def cumulative_log_return(closes: Sequence[float]) -> float:
    if len(closes) < 2:
        return 0.0
    return log_return(closes[0], closes[-1])


def simple_return(prev: float, current: float) -> float:
    if prev == 0:
        raise ValueError("simple return requires non-zero base price")
    return (current / prev) - 1.0
