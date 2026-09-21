"""Transparent mean-reversion baseline / falsification control (Section 21.6).

  short when zscore >= entry_z     (price stretched above its trailing centre)
  long  when zscore <= -entry_z
  exit  when |zscore| <= exit_z

Included to be beaten or to fail honestly. If both this and momentum_v1 look
attractive on the same sample, that is evidence about the sample, not about
either rule.
"""
from __future__ import annotations

from maysani_quant.domain.enums import Action, ReasonCode, Side
from maysani_quant.domain.models import FeatureSnapshot, PortfolioSnapshot, Signal
from maysani_quant.strategies.base import Strategy, register


@register
class MeanReversionV1(Strategy):
    strategy_id = "mean_reversion_v1"
    version = "v1.0.0"

    DEFAULTS = {
        "entry_z": 1.5,
        "exit_z": 0.5,
        "vol_filter_max": 0.02,
        "stop_atr_multiple": 2.0,
    }

    def __init__(self, params=None) -> None:
        merged = dict(self.DEFAULTS)
        merged.update(dict(params or {}))
        super().__init__(merged)

    def evaluate(self, features: FeatureSnapshot, portfolio: PortfolioSnapshot) -> Signal:
        z = features.get("zscore")
        vol = features.get("realized_vol")
        atr = features.get("atr")
        if z is None or vol is None or atr is None:
            return self._signal(features, Action.WAIT, 0.0, (ReasonCode.FEATURES_UNAVAILABLE,))

        stop_distance = atr * float(self.params["stop_atr_multiple"])
        position = portfolio.position

        if position is not None:
            if abs(z) <= float(self.params["exit_z"]):
                close_action = Action.SELL if position.side is Side.LONG else Action.BUY
                return self._signal(
                    features, close_action, z, (ReasonCode.EXIT_SIGNAL,),
                    stop_distance=stop_distance,
                )
            return self._signal(features, Action.WAIT, z, (ReasonCode.HOLD,))

        if vol > float(self.params["vol_filter_max"]):
            return self._signal(features, Action.WAIT, z, (ReasonCode.VOL_FILTER,))

        entry = float(self.params["entry_z"])
        if z >= entry:
            return self._signal(
                features, Action.SELL, -z, (ReasonCode.ENTRY_SHORT,), stop_distance=stop_distance
            )
        if z <= -entry:
            return self._signal(
                features, Action.BUY, -z, (ReasonCode.ENTRY_LONG,), stop_distance=stop_distance
            )
        return self._signal(features, Action.WAIT, -z, (ReasonCode.NO_SIGNAL,))
