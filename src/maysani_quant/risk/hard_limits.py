"""Deterministic hard risk engine (Section 12).

Gate order is fixed and blocking gates run before sizing gates, so a rejection
reason is always the *first* thing that was wrong, not whichever check happened
to be cheapest. Reducing an existing position is treated differently from
opening one: risk may always be given back, never silently added.

Sizing identity:      size = risk_budget / loss_per_unit_at_stop
Every element is instrument-aware; sizes round DOWN to the tradable step.
"""
from __future__ import annotations

from datetime import datetime

from maysani_quant.domain.enums import Action, OrganismState, ReasonCode, Side, Verdict
from maysani_quant.domain.models import (
    InstrumentSpec,
    PortfolioSnapshot,
    RiskDecision,
    Signal,
    stable_hash,
)
from maysani_quant.risk.interfaces import MarketState, RiskConfig, RiskState


class HardRiskEngine:
    """The only component permitted to authorise a position size."""

    def __init__(self, config: RiskConfig, state: RiskState | None = None) -> None:
        self.config = config
        self.state = state or RiskState()

    @property
    def config_version(self) -> str:
        return self.config.config_version

    # ------------------------------------------------------------------ state
    def start_session(self, day: str, equity: float) -> None:
        """Roll the daily-loss window. Called by the engine at date change."""
        self.state.session_date = day
        self.state.session_start_equity = equity
        self.state.realized_loss_today = 0.0

    def observe_equity(self, equity: float) -> None:
        self.state.peak_equity = max(self.state.peak_equity, equity)

    def record_realized(self, pnl: float) -> None:
        if pnl < 0:
            self.state.realized_loss_today += -pnl

    def engage_kill_switch(self, reason: str = "") -> None:
        """Idempotent. Once set, only an explicit reset clears it."""
        self.state.kill_switch = True

    # ------------------------------------------------------------------ assess
    def assess(
        self,
        signal: Signal,
        portfolio: PortfolioSnapshot,
        market: MarketState,
        instrument: InstrumentSpec,
    ) -> RiskDecision:
        reasons: list[ReasonCode] = []
        detail: dict[str, float | str | bool] = {}
        as_of = signal.as_of

        def reject(code: ReasonCode) -> RiskDecision:
            self.state.reject_counts[code.value] = (
                self.state.reject_counts.get(code.value, 0) + 1
            )
            return self._decision(
                as_of, Verdict.REJECT, 0.0, 0.0, signal.stop_distance, (code, *reasons), detail
            )

        if signal.action is Action.WAIT:
            # A WAIT still produces a risk decision so the journal has one shape.
            return self._decision(
                as_of, Verdict.REJECT, 0.0, 0.0, signal.stop_distance, (ReasonCode.NO_SIGNAL,), detail
            )

        is_reducing = self._is_reducing(signal, portfolio)
        detail["is_reducing"] = is_reducing

        # --- gates that apply even when flattening -------------------------
        if portfolio.state is OrganismState.DEAD:
            return reject(ReasonCode.ORGANISM_DEAD)
        if not market.data_quality_ok:
            return reject(ReasonCode.DATA_QUALITY_FAIL)
        if market.staleness_bars > self.config.max_staleness_bars:
            detail["staleness_bars"] = market.staleness_bars
            return reject(ReasonCode.DATA_STALE)
        if not market.system_healthy:
            return reject(ReasonCode.SYSTEM_UNHEALTHY)

        if is_reducing:
            # Closing risk is always permitted once data and system are sane.
            size = self._round(abs(portfolio.position.units), instrument)
            return self._decision(
                as_of, Verdict.APPROVE, size, size, signal.stop_distance,
                (ReasonCode.OK,), detail | {"reduce_only": True},
            )

        # --- gates that block NEW risk only --------------------------------
        if self.state.kill_switch:
            return reject(ReasonCode.KILL_SWITCH_ACTIVE)
        if portfolio.equity <= 0:
            return reject(ReasonCode.EQUITY_NON_POSITIVE)
        if market.spread > self.config.max_spread_price:
            detail["spread"] = market.spread
            return reject(ReasonCode.SPREAD_TOO_WIDE)
        if market.realized_vol is not None and market.realized_vol > self.config.max_realized_vol:
            detail["realized_vol"] = market.realized_vol
            return reject(ReasonCode.VOLATILITY_UNSAFE)
        if market.in_event_window and self.config.event_window_blocks_entry:
            return reject(ReasonCode.EVENT_RISK_WINDOW)

        drawdown = portfolio.drawdown
        if drawdown >= self.config.max_drawdown_pct:
            detail["drawdown"] = drawdown
            return reject(ReasonCode.MAX_DRAWDOWN)

        if self.state.session_start_equity > 0:
            loss_pct = self.state.realized_loss_today / self.state.session_start_equity
            if loss_pct >= self.config.daily_loss_limit_pct:
                detail["daily_loss_pct"] = loss_pct
                return reject(ReasonCode.DAILY_LOSS_LIMIT)

        # Only one instrument in V0.1, so an open position is the cluster limit.
        if portfolio.position is not None:
            return reject(ReasonCode.CORRELATION_CLUSTER_LIMIT)

        stop_distance = signal.stop_distance
        if stop_distance is None or stop_distance <= 0:
            return reject(ReasonCode.STOP_DISTANCE_INVALID)
        if stop_distance < self.config.min_stop_distance_price:
            detail["stop_distance"] = stop_distance
            return reject(ReasonCode.STOP_DISTANCE_INVALID)
        if stop_distance > self.config.max_stop_distance_price:
            detail["stop_distance"] = stop_distance
            return reject(ReasonCode.STOP_DISTANCE_INVALID)

        # --- sizing ---------------------------------------------------------
        equity = portfolio.equity
        risk_budget = equity * self.config.risk_per_trade_pct

        # Loss at stop must include the cost of crossing the spread to get out.
        loss_per_unit = (stop_distance + market.spread) * instrument.contract_multiplier
        if loss_per_unit <= 0:
            return reject(ReasonCode.STOP_DISTANCE_INVALID)

        requested = risk_budget / loss_per_unit
        detail["risk_budget"] = risk_budget
        detail["loss_per_unit_at_stop"] = loss_per_unit
        size = requested
        reasons.append(ReasonCode.SIZE_REDUCED_PER_TRADE_RISK)

        # drawdown throttle
        multiplier, throttled = self.config.throttle_multiplier(drawdown)
        if throttled:
            size *= multiplier
            detail["drawdown_throttle"] = multiplier
            reasons.append(ReasonCode.SIZE_REDUCED_DRAWDOWN_THROTTLE)

        # volatility targeting (optional, off by default)
        if self.config.vol_target and market.realized_vol and market.realized_vol > 0:
            scale = min(1.0, self.config.vol_target / market.realized_vol)
            if scale < 1.0:
                size *= scale
                detail["vol_scale"] = scale
                reasons.append(ReasonCode.SIZE_REDUCED_VOLATILITY)

        price = market.reference_price
        if price <= 0:
            return reject(ReasonCode.DATA_QUALITY_FAIL)

        # leverage cap on notional
        max_notional = equity * self.config.max_leverage
        max_units_leverage = max_notional / (price * instrument.contract_multiplier)
        if size > max_units_leverage:
            size = max_units_leverage
            detail["max_units_leverage"] = max_units_leverage
            reasons.append(ReasonCode.SIZE_REDUCED_LEVERAGE)

        # margin headroom
        usable_margin = equity * self.config.max_margin_utilisation
        margin_per_unit = price * instrument.contract_multiplier * self.config.margin_requirement_pct
        if margin_per_unit > 0:
            max_units_margin = usable_margin / margin_per_unit
            if size > max_units_margin:
                size = max_units_margin
                detail["max_units_margin"] = max_units_margin
                reasons.append(ReasonCode.SIZE_REDUCED_MARGIN)

        # aggregate open risk across the book (one position in V0.1, but the
        # check is written against the aggregate so it stays correct later)
        max_open_risk = equity * self.config.max_open_risk_pct
        open_risk_used = 0.0  # no other positions by construction
        remaining_risk = max_open_risk - open_risk_used
        if remaining_risk <= 0:
            return reject(ReasonCode.EXPOSURE_LIMIT)
        max_units_open_risk = remaining_risk / loss_per_unit
        if size > max_units_open_risk:
            size = max_units_open_risk
            detail["max_units_open_risk"] = max_units_open_risk
            reasons.append(ReasonCode.SIZE_REDUCED_MAX_OPEN_RISK)

        approved = self._round(size, instrument)
        detail["requested_size"] = requested
        detail["approved_size"] = approved

        if approved < instrument.min_order_size or approved <= 0:
            detail["min_order_size"] = instrument.min_order_size
            return reject(ReasonCode.SIZE_BELOW_MIN)

        # Final invariant re-check on the rounded size. Rounding down can only
        # reduce risk, but the assertion is cheap and this is the last gate.
        final_notional = approved * price * instrument.contract_multiplier
        if final_notional > max_notional * (1 + 1e-9):
            return reject(ReasonCode.EXPOSURE_LIMIT)
        if approved * loss_per_unit > max_open_risk * (1 + 1e-9):
            return reject(ReasonCode.EXPOSURE_LIMIT)

        verdict = (
            Verdict.APPROVE
            if abs(approved - requested) <= instrument.size_step * 0.5
            else Verdict.APPROVE_WITH_REDUCED_SIZE
        )
        codes = tuple(reasons) if reasons else (ReasonCode.OK,)
        return self._decision(
            as_of, verdict, approved, requested, stop_distance, codes, detail
        )

    # ----------------------------------------------------------------- helpers
    @staticmethod
    def _is_reducing(signal: Signal, portfolio: PortfolioSnapshot) -> bool:
        position = portfolio.position
        if position is None:
            return False
        if position.side is Side.LONG and signal.action is Action.SELL:
            return True
        if position.side is Side.SHORT and signal.action is Action.BUY:
            return True
        return False

    @staticmethod
    def _round(size: float, instrument: InstrumentSpec) -> float:
        return instrument.round_size_down(size)

    def _decision(
        self,
        as_of: datetime,
        verdict: Verdict,
        approved: float,
        requested: float,
        stop_distance: float | None,
        reasons: tuple[ReasonCode, ...],
        detail: dict,
    ) -> RiskDecision:
        self.state.decisions_emitted += 1
        decision_id = stable_hash(
            {
                "as_of": as_of.isoformat(),
                "verdict": verdict.value,
                "approved": round(approved, 10),
                "requested": round(requested, 10),
                "seq": self.state.decisions_emitted,
                "config_version": self.config.config_version,
            }
        )[:32]
        return RiskDecision(
            decision_id=decision_id,
            as_of=as_of,
            verdict=verdict,
            approved_size=approved,
            requested_size=requested,
            stop_distance=stop_distance,
            risk_config_version=self.config.config_version,
            reason_codes=reasons,
            detail=detail,
        )
