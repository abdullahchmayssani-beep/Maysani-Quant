"""Transparent trend/momentum baseline (Section 21.6).

Rules, in full:
  long  when ma_spread >= entry_threshold and realized_vol <= vol_filter_max
  short when ma_spread <= -entry_threshold and the same vol filter passes
  exit  when |ma_spread| falls below exit_threshold, or the position side
        disagrees with the current spread sign

Four parameters, all predeclared in config and hashed into the experiment
record. No optimiser is bundled with this file on purpose.
"""
from __future__ import annotations

from maysani_quant.domain.enums import Action, ReasonCode, Side
from maysani_quant.domain.models import FeatureSnapshot, PortfolioSnapshot, Signal
from maysani_quant.strategies.base import Strategy, register


@register
class MomentumV1(Strategy):
    strategy_id = "momentum_v1"
    version = "v1.0.0"

    DEFAULTS = {
        "entry_threshold": 0.002,
        "exit_threshold": 0.0005,
        "vol_filter_max": 0.02,
        "stop_atr_multiple": 2.0,
    }

    def __init__(self, params=None) -> None:
        merged = dict(self.DEFAULTS)
        merged.update(dict(params or {}))
        super().__init__(merged)

    def evaluate(self, features: FeatureSnapshot, portfolio: PortfolioSnapshot) -> Signal:
        spread = features.get("ma_spread")
        vol = features.get("realized_vol")
        atr = features.get("atr")
        if spread is None or vol is None or atr is None:
            return self._signal(features, Action.WAIT, 0.0, (ReasonCode.FEATURES_UNAVAILABLE,))

        stop_distance = atr * float(self.params["stop_atr_multiple"])
        entry = float(self.params["entry_threshold"])
        exit_level = float(self.params["exit_threshold"])
        position = portfolio.position

        if position is not None:
            wrong_way = (position.side is Side.LONG and spread < 0) or (
                position.side is Side.SHORT and spread > 0
            )
            if abs(spread) < exit_level or wrong_way:
                close_action = Action.SELL if position.side is Side.LONG else Action.BUY
                return self._signal(
                    features, close_action, spread, (ReasonCode.EXIT_SIGNAL,),
                    stop_distance=stop_distance,
                )
            return self._signal(features, Action.WAIT, spread, (ReasonCode.HOLD,))

        if vol > float(self.params["vol_filter_max"]):
            return self._signal(features, Action.WAIT, spread, (ReasonCode.VOL_FILTER,))

        if spread >= entry:
            return self._signal(
                features, Action.BUY, spread, (ReasonCode.ENTRY_LONG,), stop_distance=stop_distance
            )
        if spread <= -entry:
            return self._signal(
                features, Action.SELL, spread, (ReasonCode.ENTRY_SHORT,), stop_distance=stop_distance
            )
        return self._signal(features, Action.WAIT, spread, (ReasonCode.NO_SIGNAL,))
