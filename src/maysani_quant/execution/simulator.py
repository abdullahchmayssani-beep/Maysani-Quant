"""Simulated execution kernel (Sections 13.1-13.3, 21.5).

Timing contract, enforced here and nowhere else:
  * a decision made at the close of bar t may only fill at the OPEN of bar t+1
  * the fill price uses the executable side plus configured slippage
  * the decision bar's close is never used as a fill price

Ambiguous intrabar paths: when both the stop and an exit level sit inside the
same bar's range and the path is unknown, `ADVERSE` assumes the stop was hit
first. `SKIP` refuses to resolve the bar at all. There is no third option that
picks the favourable outcome.
"""
from __future__ import annotations

from datetime import datetime

from maysani_quant.domain.enums import (
    Action,
    AmbiguousBarPolicy,
    FillStatus,
    OrderType,
    ReasonCode,
    Side,
    Verdict,
)
from maysani_quant.domain.models import (
    Fill,
    InstrumentSpec,
    MarketBar,
    OrderIntent,
    Position,
    RiskDecision,
    stable_hash,
)
from maysani_quant.execution.costs import CostModel


class RiskBypassError(RuntimeError):
    """Raised if anything tries to execute without an approving RiskDecision.

    This is the downstream half of the risk veto: the engine cannot merely
    *decline* to pass a REJECT along, it is structurally unable to act on one.
    """


class ExecutionSimulator:
    def __init__(
        self,
        cost_model: CostModel,
        instrument: InstrumentSpec,
        ambiguous_policy: AmbiguousBarPolicy = AmbiguousBarPolicy.ADVERSE,
    ) -> None:
        self.costs = cost_model
        self.instrument = instrument
        self.ambiguous_policy = ambiguous_policy
        self._intent_seq = 0

    # ------------------------------------------------------------------ orders
    def build_intent(
        self,
        risk_decision: RiskDecision,
        action: Action,
        instrument: str,
        created_at: datetime,
        parent_decision_id: str,
        is_reducing: bool = False,
    ) -> OrderIntent:
        """The ONLY constructor of OrderIntent in the codebase."""
        if risk_decision.verdict is Verdict.REJECT or not risk_decision.permits_order:
            raise RiskBypassError(
                f"refusing to build an order from verdict={risk_decision.verdict.value} "
                f"reasons={[r.value for r in risk_decision.reason_codes]}"
            )
        if action is Action.WAIT:
            raise RiskBypassError("WAIT cannot produce an order intent")
        self._intent_seq += 1
        intent_id = stable_hash(
            {
                "risk_decision_id": risk_decision.decision_id,
                "seq": self._intent_seq,
                "action": action.value,
                "size": round(risk_decision.approved_size, 10),
            }
        )[:32]
        return OrderIntent(
            intent_id=intent_id,
            created_at=created_at,
            instrument=instrument,
            action=action,
            size=risk_decision.approved_size,
            order_type=OrderType.MARKET,
            decision_id=parent_decision_id,
            risk_decision_id=risk_decision.decision_id,
            is_reducing=is_reducing,
        )

    def submit(self, intent: OrderIntent, fill_bar: MarketBar) -> list[Fill]:
        """Fill at the open of the NEXT bar - never at the decision bar's close."""
        if intent.size <= 0:
            return [
                Fill(
                    intent_id=intent.intent_id,
                    timestamp=fill_bar.start_time,
                    instrument=intent.instrument,
                    action=intent.action,
                    price=fill_bar.open,
                    size=0.0,
                    status=FillStatus.REJECTED,
                    reference_price=fill_bar.open,
                    reason="non-positive size",
                )
            ]
        priced = self.costs.execution_price(
            intent.action, fill_bar.open, intent.size, fill_bar.spread
        )
        return [
            Fill(
                intent_id=intent.intent_id,
                timestamp=fill_bar.start_time,
                instrument=intent.instrument,
                action=intent.action,
                price=self.instrument.round_price(priced.price),
                size=intent.size,
                status=FillStatus.FILLED,
                reference_price=priced.reference_price,
                spread_cost=priced.spread_cost,
                slippage_cost=priced.slippage_cost,
                commission=priced.commission,
                reason=ReasonCode.OK.value,
            )
        ]

    # ------------------------------------------------------------------- stops
    def resolve_stop(
        self, position: Position, bar: MarketBar
    ) -> tuple[bool, float | None, str]:
        """Did this bar hit the stop, and at what assumed price?

        Returns (hit, assumed_exit_price, note). Gap handling is explicit: if
        the bar opens through the stop, the fill is assumed at the open, which
        is worse than the stop level. Pretending the stop filled at its level
        through a gap is exactly the kind of free money this engine refuses to
        print.
        """
        if position.stop_price is None:
            return False, None, ""
        stop = position.stop_price
        spread = self.costs.spread_for(bar.spread)
        half = spread / 2.0

        if position.side is Side.LONG:
            # Long exits at the bid: bid = mid - half.
            if bar.open - half <= stop:
                return True, bar.open - half, "gap_through_stop_at_open"
            if bar.low - half <= stop:
                if self.ambiguous_policy is AmbiguousBarPolicy.SKIP:
                    return False, None, "ambiguous_bar_skipped"
                return True, stop, "stop_assumed_hit_adverse"
            return False, None, ""

        # Short exits at the ask: ask = mid + half.
        if bar.open + half >= stop:
            return True, bar.open + half, "gap_through_stop_at_open"
        if bar.high + half >= stop:
            if self.ambiguous_policy is AmbiguousBarPolicy.SKIP:
                return False, None, "ambiguous_bar_skipped"
            return True, stop, "stop_assumed_hit_adverse"
        return False, None, ""

    def stop_fill(
        self, position: Position, bar: MarketBar, exit_price: float, note: str
    ) -> Fill:
        action = Action.SELL if position.side is Side.LONG else Action.BUY
        units = position.units
        spread = self.costs.spread_for(bar.spread)
        self._intent_seq += 1
        intent_id = stable_hash(
            {"stop": True, "seq": self._intent_seq, "t": bar.end_time.isoformat()}
        )[:32]
        return Fill(
            intent_id=intent_id,
            timestamp=bar.end_time,
            instrument=bar.instrument,
            action=action,
            price=self.instrument.round_price(exit_price),
            size=units,
            status=FillStatus.FILLED,
            reference_price=exit_price,
            spread_cost=(spread / 2.0) * units,
            slippage_cost=0.0,
            commission=self.costs.commission(units),
            reason=f"STOP:{note}",
        )
