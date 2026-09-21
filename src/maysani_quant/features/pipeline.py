"""Feature pipeline.

Takes a PointInTimeView and returns a FeatureSnapshot. The pipeline never sees
the bar being decided *into* - only bars whose available_time has passed.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from maysani_quant.data.interfaces import PointInTimeView
from maysani_quant.domain.models import FeatureSnapshot, stable_hash
from maysani_quant.features.mean_reversion import rolling_zscore
from maysani_quant.features.momentum import ma_spread, momentum_log_return, moving_average
from maysani_quant.features.volatility import average_true_range, realized_volatility

FEATURE_CODE_VERSION = "features-v0.1.0"


@dataclass(frozen=True)
class FeatureConfig:
    momentum_lookback: int = 20
    ma_fast: int = 10
    ma_slow: int = 50
    vol_lookback: int = 20
    zscore_lookback: int = 20
    atr_lookback: int = 14

    @property
    def warmup_bars(self) -> int:
        """Bars required before any feature is defined. Below this: WAIT/WARMUP."""
        return (
            max(
                self.momentum_lookback + 1,
                self.ma_slow,
                self.vol_lookback + 1,
                self.zscore_lookback + 1,
                self.atr_lookback + 1,
            )
            + 1
        )


class FeaturePipeline:
    def __init__(self, config: FeatureConfig) -> None:
        self.config = config

    def warmup_bars(self) -> int:
        return self.config.warmup_bars

    def compute(self, view: PointInTimeView, as_of: datetime) -> FeatureSnapshot | None:
        """Return None while warming up. Never partially-filled feature sets."""
        cfg = self.config
        bars = view.bars
        if len(bars) < cfg.warmup_bars:
            return None
        closes = [b.close for b in bars]

        values = {
            "close": closes[-1],
            "momentum_logret": momentum_log_return(closes, cfg.momentum_lookback),
            "ma_fast": moving_average(closes, cfg.ma_fast),
            "ma_slow": moving_average(closes, cfg.ma_slow),
            "ma_spread": ma_spread(closes, cfg.ma_fast, cfg.ma_slow),
            "realized_vol": realized_volatility(closes[-(cfg.vol_lookback + 1) :]),
            "zscore": rolling_zscore(closes, cfg.zscore_lookback),
            "atr": average_true_range(bars, cfg.atr_lookback),
        }
        snapshot_id = stable_hash(
            {
                "as_of": as_of.isoformat(),
                "instrument": view.instrument,
                "values": {k: round(v, 12) for k, v in values.items()},
                "code_version": FEATURE_CODE_VERSION,
                "config": cfg.__dict__,
            }
        )[:32]
        return FeatureSnapshot(
            snapshot_id=snapshot_id,
            as_of=as_of,
            instrument=view.instrument,
            values=values,
            input_bar_count=len(bars),
            last_input_available_time=bars[-1].available_time,
            code_version=FEATURE_CODE_VERSION,
        )
