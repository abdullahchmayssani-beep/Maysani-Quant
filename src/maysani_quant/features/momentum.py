"""Momentum / trend features. Few, predeclared parameters (Section 21.6)."""
from __future__ import annotations

from collections.abc import Sequence

from maysani_quant.features.returns import cumulative_log_return


def moving_average(values: Sequence[float], window: int) -> float:
    if len(values) < window:
        raise ValueError(f"moving average needs {window} values, got {len(values)}")
    tail = values[-window:]
    return sum(tail) / window


def ma_spread(closes: Sequence[float], fast: int, slow: int) -> float:
    """(fast MA - slow MA) / slow MA. Scale-free, so thresholds transfer."""
    if slow <= fast:
        raise ValueError("slow window must exceed fast window")
    slow_ma = moving_average(closes, slow)
    if slow_ma == 0:
        raise ValueError("slow moving average is zero")
    return (moving_average(closes, fast) - slow_ma) / slow_ma


def momentum_log_return(closes: Sequence[float], lookback: int) -> float:
    if len(closes) < lookback + 1:
        raise ValueError(f"momentum needs {lookback + 1} closes, got {len(closes)}")
    return cumulative_log_return(closes[-(lookback + 1) :])
