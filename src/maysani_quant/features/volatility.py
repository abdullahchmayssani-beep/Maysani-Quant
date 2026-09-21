"""Volatility and range features.

ATR here is a *stop-distance* input for the risk engine, not a forecast. It is
computed from completed bars only.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

from maysani_quant.domain.models import MarketBar
from maysani_quant.features.returns import log_returns


def realized_volatility(closes: Sequence[float], annualisation: float | None = None) -> float:
    """Sample standard deviation of log returns over the supplied window."""
    rets = log_returns(closes)
    if len(rets) < 2:
        return 0.0
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    sd = math.sqrt(var)
    if annualisation:
        sd *= math.sqrt(annualisation)
    return sd


def true_range(bar: MarketBar, prev_close: float | None) -> float:
    if prev_close is None:
        return bar.high - bar.low
    return max(
        bar.high - bar.low,
        abs(bar.high - prev_close),
        abs(bar.low - prev_close),
    )


def average_true_range(bars: Sequence[MarketBar], lookback: int) -> float:
    """Simple (non-Wilder) mean of true range over `lookback` completed bars."""
    if len(bars) < lookback + 1:
        raise ValueError(f"ATR needs {lookback + 1} bars, got {len(bars)}")
    window = bars[-(lookback + 1) :]
    trs = [true_range(window[i], window[i - 1].close) for i in range(1, len(window))]
    return sum(trs) / len(trs)
