"""Permanent controls (Section 13.7).

These exist so that no candidate strategy is ever reported without something
boring beside it. They are not competitors; they are the null hypotheses.
"""
from __future__ import annotations

from maysani_quant.domain.enums import Action, ReasonCode
from maysani_quant.domain.models import FeatureSnapshot, PortfolioSnapshot, Signal
from maysani_quant.strategies.base import Strategy, register


@register
class NoTradeV1(Strategy):
    """WAIT on every bar. The control every other strategy must beat net of costs."""

    strategy_id = "no_trade_v1"
    version = "v1.0.0"

    def evaluate(self, features: FeatureSnapshot, portfolio: PortfolioSnapshot) -> Signal:
        return self._signal(features, Action.WAIT, 0.0, (ReasonCode.NO_SIGNAL,))


@register
class BuyAndHoldV1(Strategy):
    """Long exposure from the first eligible bar; never exits.

    For a currency pair this is 'hold the base currency', not a market return.
    It is included because a directional drift in the sample would otherwise be
    mistaken for skill.
    """

    strategy_id = "buy_and_hold_v1"
    version = "v1.1.0"

    # The risk engine refuses any entry without a stop distance, so a truly
    # stopless hold is not expressible - and should not be. A wide protective
    # stop is used instead; after a stop-out the control re-enters on the next
    # bar. v1.0.0 had no default stop and was vetoed on every bar, making it
    # indistinguishable from no_trade_v1 (see tests/regression).
    DEFAULTS = {"stop_atr_multiple": 5.0}

    def __init__(self, params=None) -> None:
        merged = dict(self.DEFAULTS)
        merged.update(dict(params or {}))
        super().__init__(merged)

    def evaluate(self, features: FeatureSnapshot, portfolio: PortfolioSnapshot) -> Signal:
        if portfolio.position is not None:
            return self._signal(features, Action.WAIT, 1.0, (ReasonCode.HOLD,))
        atr = features.get("atr") or 0.0
        stop_mult = float(self.params.get("stop_atr_multiple", 0.0))
        stop = atr * stop_mult if stop_mult > 0 else None
        return self._signal(
            features, Action.BUY, 1.0, (ReasonCode.ENTRY_LONG,), stop_distance=stop
        )
