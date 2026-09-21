"""Risk engine tests (Section 12, 21.9).

These are the tests that matter most for the project's stated authority model.
A REJECT must be structurally unable to become an order, and every reduction
must emit a reason code that survives into the journal.
"""
from __future__ import annotations

import pytest

from maysani_quant.domain.enums import (
    Action,
    OrganismState,
    ReasonCode,
    Side,
    Verdict,
)
from maysani_quant.domain.models import (
    InstrumentSpec,
    PortfolioSnapshot,
    Position,
    Signal,
)
from maysani_quant.execution.simulator import ExecutionSimulator, RiskBypassError
from maysani_quant.risk.hard_limits import HardRiskEngine
from maysani_quant.risk.interfaces import MarketState, RiskConfig, RiskState
from tests.conftest import START


def snapshot(
    equity: float = 50.0,
    position: Position | None = None,
    drawdown: float = 0.0,
    state: OrganismState = OrganismState.ALIVE,
    peak: float | None = None,
) -> PortfolioSnapshot:
    return PortfolioSnapshot(
        timestamp=START,
        cash=equity,
        unrealized_pnl=0.0,
        equity=equity,
        gross_notional=0.0,
        net_notional=0.0,
        leverage=0.0,
        margin_used=0.0,
        margin_free=equity,
        peak_equity=peak if peak is not None else equity,
        drawdown=drawdown,
        state=state,
        position=position,
    )


def signal(action: Action = Action.BUY, stop: float | None = 0.004) -> Signal:
    return Signal(
        as_of=START,
        instrument="EURUSD",
        strategy_id="test",
        strategy_version="v1",
        action=action,
        score=1.0,
        horizon_bars=1,
        snapshot_id="snap",
        stop_distance=stop,
    )


def market(
    spread: float = 0.0002,
    price: float = 1.10,
    vol: float = 0.005,
    staleness: float = 0.0,
    quality_ok: bool = True,
    healthy: bool = True,
    event: bool = False,
) -> MarketState:
    return MarketState(
        as_of=START,
        instrument="EURUSD",
        reference_price=price,
        spread=spread,
        atr=0.002,
        realized_vol=vol,
        staleness_bars=staleness,
        data_quality_ok=quality_ok,
        system_healthy=healthy,
        in_event_window=event,
    )


@pytest.mark.invariant
def test_sizing_identity_risk_budget_over_loss_at_stop(instrument: InstrumentSpec):
    """size = (equity * risk_pct) / (stop_distance + spread), rounded down.

    Margin and leverage headroom are made generous here so the per-trade risk
    gate is the only binding constraint and the identity is testable in
    isolation. See the next test for what actually binds at USD 50.
    """
    config = RiskConfig(
        risk_per_trade_pct=0.01,
        max_leverage=50.0,
        margin_requirement_pct=0.01,
        max_margin_utilisation=1.0,
        max_open_risk_pct=1.0,
    )
    engine = HardRiskEngine(config)
    stop, spread, equity = 0.004, 0.0002, 50.0
    decision = engine.assess(signal(stop=stop), snapshot(equity), market(spread), instrument)

    expected = (equity * config.risk_per_trade_pct) / (stop + spread)
    assert decision.verdict is not Verdict.REJECT
    assert decision.approved_size == pytest.approx(
        instrument.round_size_down(expected), abs=1e-9
    )
    assert decision.approved_size <= expected, "rounding must never round risk up"


@pytest.mark.invariant
def test_margin_gate_binds_before_risk_budget_at_fifty_dollars(
    risk_config: RiskConfig, instrument: InstrumentSpec
):
    """A recorded V0.1 finding, not a preference.

    With the provisional defaults (20% margin requirement, 50% max utilisation)
    a USD 50 account is margin-constrained before it is risk-constrained: the
    1% stop-risk budget would allow ~119 units, margin allows ~113. This is
    exactly the "USD 50 feasibility" question in Section 23, and it is pinned
    here so a later config change that flips which gate binds shows up as a
    failing test rather than as a quietly different backtest.
    """
    engine = HardRiskEngine(risk_config)
    stop, spread, equity, price = 0.004, 0.0002, 50.0, 1.10
    decision = engine.assess(signal(stop=stop), snapshot(equity), market(spread, price), instrument)

    risk_budget_units = (equity * risk_config.risk_per_trade_pct) / (stop + spread)
    margin_units = (equity * risk_config.max_margin_utilisation) / (
        price * risk_config.margin_requirement_pct
    )
    assert margin_units < risk_budget_units, "expected margin to be the tighter gate"
    assert decision.approved_size == pytest.approx(
        instrument.round_size_down(margin_units), abs=1e-9
    )
    assert ReasonCode.SIZE_REDUCED_MARGIN in decision.reason_codes


@pytest.mark.invariant
def test_loss_at_stop_never_exceeds_risk_budget(
    risk_config: RiskConfig, instrument: InstrumentSpec
):
    engine = HardRiskEngine(risk_config)
    for stop in (0.0005, 0.001, 0.004, 0.01, 0.03):
        decision = engine.assess(signal(stop=stop), snapshot(50.0), market(), instrument)
        if decision.verdict is Verdict.REJECT:
            continue
        loss_at_stop = decision.approved_size * (stop + 0.0002)
        budget = 50.0 * risk_config.risk_per_trade_pct
        assert loss_at_stop <= budget + 1e-9, f"stop={stop} breached the risk budget"


@pytest.mark.invariant
def test_leverage_cap_is_enforced(instrument: InstrumentSpec):
    """A tiny stop implies a huge size; leverage must clamp it."""
    config = RiskConfig(risk_per_trade_pct=0.50, max_leverage=2.0, max_open_risk_pct=1.0,
                        min_stop_distance_price=0.00001)
    engine = HardRiskEngine(config)
    decision = engine.assess(signal(stop=0.00002), snapshot(50.0), market(spread=0.0), instrument)
    notional = decision.approved_size * 1.10
    assert notional <= 50.0 * 2.0 + 1e-6
    assert ReasonCode.SIZE_REDUCED_LEVERAGE in decision.reason_codes
    assert decision.verdict is Verdict.APPROVE_WITH_REDUCED_SIZE


@pytest.mark.invariant
def test_margin_headroom_is_enforced(instrument: InstrumentSpec):
    config = RiskConfig(
        risk_per_trade_pct=0.50, max_leverage=100.0, margin_requirement_pct=0.50,
        max_margin_utilisation=0.10, max_open_risk_pct=1.0, min_stop_distance_price=0.00001,
    )
    engine = HardRiskEngine(config)
    decision = engine.assess(signal(stop=0.00002), snapshot(50.0), market(spread=0.0), instrument)
    margin = decision.approved_size * 1.10 * 0.50
    assert margin <= 50.0 * 0.10 + 1e-6


@pytest.mark.invariant
def test_reject_cannot_become_an_order(
    risk_config: RiskConfig, instrument: InstrumentSpec, cost_model
):
    """The downstream half of the veto (Section 12 invariant 2)."""
    engine = HardRiskEngine(risk_config)
    decision = engine.assess(signal(), snapshot(50.0), market(quality_ok=False), instrument)
    assert decision.verdict is Verdict.REJECT

    simulator = ExecutionSimulator(cost_model, instrument)
    with pytest.raises(RiskBypassError):
        simulator.build_intent(decision, Action.BUY, "EURUSD", START, "dec-1")


@pytest.mark.invariant
def test_wait_cannot_become_an_order(risk_config: RiskConfig, instrument, cost_model):
    engine = HardRiskEngine(risk_config)
    decision = engine.assess(signal(Action.WAIT), snapshot(50.0), market(), instrument)
    assert decision.verdict is Verdict.REJECT
    simulator = ExecutionSimulator(cost_model, instrument)
    with pytest.raises(RiskBypassError):
        simulator.build_intent(decision, Action.WAIT, "EURUSD", START, "dec-1")


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        ({"quality_ok": False}, ReasonCode.DATA_QUALITY_FAIL),
        ({"staleness": 99.0}, ReasonCode.DATA_STALE),
        ({"healthy": False}, ReasonCode.SYSTEM_UNHEALTHY),
        ({"spread": 0.01}, ReasonCode.SPREAD_TOO_WIDE),
        ({"vol": 0.99}, ReasonCode.VOLATILITY_UNSAFE),
        ({"event": True}, ReasonCode.EVENT_RISK_WINDOW),
    ],
)
def test_blocking_gates_emit_their_reason_code(
    risk_config: RiskConfig, instrument: InstrumentSpec, kwargs, expected
):
    engine = HardRiskEngine(risk_config)
    decision = engine.assess(signal(), snapshot(50.0), market(**kwargs), instrument)
    assert decision.verdict is Verdict.REJECT
    assert expected in decision.reason_codes


@pytest.mark.invariant
def test_dead_organism_is_refused_new_risk(risk_config: RiskConfig, instrument: InstrumentSpec):
    engine = HardRiskEngine(risk_config)
    decision = engine.assess(
        signal(), snapshot(1.0, state=OrganismState.DEAD), market(), instrument
    )
    assert decision.verdict is Verdict.REJECT
    assert ReasonCode.ORGANISM_DEAD in decision.reason_codes


@pytest.mark.invariant
def test_max_drawdown_blocks_new_risk(risk_config: RiskConfig, instrument: InstrumentSpec):
    engine = HardRiskEngine(risk_config)
    decision = engine.assess(signal(), snapshot(40.0, drawdown=0.25, peak=53.0), market(), instrument)
    assert decision.verdict is Verdict.REJECT
    assert ReasonCode.MAX_DRAWDOWN in decision.reason_codes


def test_drawdown_throttle_reduces_size(risk_config: RiskConfig, instrument: InstrumentSpec):
    engine = HardRiskEngine(risk_config)
    full = engine.assess(signal(), snapshot(50.0, drawdown=0.0), market(), instrument)
    throttled = engine.assess(
        signal(), snapshot(50.0, drawdown=0.12, peak=57.0), market(), instrument
    )
    assert throttled.approved_size < full.approved_size
    assert ReasonCode.SIZE_REDUCED_DRAWDOWN_THROTTLE in throttled.reason_codes


@pytest.mark.invariant
def test_daily_loss_limit_blocks_new_risk(risk_config: RiskConfig, instrument: InstrumentSpec):
    engine = HardRiskEngine(risk_config)
    engine.start_session("2024-01-01", 50.0)
    engine.record_realized(-2.0)   # 4% of 50, limit is 3%
    decision = engine.assess(signal(), snapshot(48.0), market(), instrument)
    assert decision.verdict is Verdict.REJECT
    assert ReasonCode.DAILY_LOSS_LIMIT in decision.reason_codes


@pytest.mark.invariant
def test_kill_switch_is_idempotent_and_blocks(risk_config: RiskConfig, instrument: InstrumentSpec):
    engine = HardRiskEngine(risk_config)
    engine.engage_kill_switch("test")
    engine.engage_kill_switch("test again")
    decision = engine.assess(signal(), snapshot(50.0), market(), instrument)
    assert ReasonCode.KILL_SWITCH_ACTIVE in decision.reason_codes


@pytest.mark.invariant
def test_closing_a_position_is_permitted_even_when_new_risk_is_blocked(
    risk_config: RiskConfig, instrument: InstrumentSpec
):
    """Risk may always be given back. A drawdown halt must not trap a position."""
    engine = HardRiskEngine(risk_config)
    engine.engage_kill_switch("halt")
    position = Position(
        instrument="EURUSD", side=Side.LONG, units=25.0, average_price=1.10, opened_at=START
    )
    decision = engine.assess(
        signal(Action.SELL), snapshot(40.0, position=position, drawdown=0.30), market(), instrument
    )
    assert decision.verdict is Verdict.APPROVE
    assert decision.approved_size == pytest.approx(25.0)


def test_second_position_is_blocked_by_cluster_gate(
    risk_config: RiskConfig, instrument: InstrumentSpec
):
    engine = HardRiskEngine(risk_config)
    position = Position(
        instrument="EURUSD", side=Side.LONG, units=10.0, average_price=1.10, opened_at=START
    )
    decision = engine.assess(signal(Action.BUY), snapshot(50.0, position=position), market(), instrument)
    assert decision.verdict is Verdict.REJECT
    assert ReasonCode.CORRELATION_CLUSTER_LIMIT in decision.reason_codes


@pytest.mark.parametrize("stop", [None, 0.0, -0.001, 0.0000001, 10.0])
def test_invalid_stop_distance_is_rejected(
    risk_config: RiskConfig, instrument: InstrumentSpec, stop
):
    engine = HardRiskEngine(risk_config)
    decision = engine.assess(signal(stop=stop), snapshot(50.0), market(), instrument)
    assert decision.verdict is Verdict.REJECT
    assert ReasonCode.STOP_DISTANCE_INVALID in decision.reason_codes


def test_size_below_minimum_is_rejected_not_rounded_up(instrument: InstrumentSpec):
    """A $50 account with a wide stop can imply < 1 unit. That is a REJECT."""
    config = RiskConfig(risk_per_trade_pct=0.0001, max_stop_distance_price=0.05)
    engine = HardRiskEngine(config)
    decision = engine.assess(signal(stop=0.04), snapshot(50.0), market(), instrument)
    assert decision.verdict is Verdict.REJECT
    assert ReasonCode.SIZE_BELOW_MIN in decision.reason_codes


@pytest.mark.invariant
def test_risk_state_survives_a_restart(risk_config: RiskConfig):
    engine = HardRiskEngine(risk_config)
    engine.start_session("2024-01-01", 50.0)
    engine.record_realized(-1.0)
    engine.observe_equity(49.0)
    payload = engine.state.to_dict()

    restored = HardRiskEngine(risk_config, RiskState.from_dict(payload))
    assert restored.state.realized_loss_today == pytest.approx(1.0)
    assert restored.state.session_date == "2024-01-01"
    assert restored.state.peak_equity == pytest.approx(49.0)


def test_reject_counts_are_recorded_for_later_analysis(
    risk_config: RiskConfig, instrument: InstrumentSpec
):
    engine = HardRiskEngine(risk_config)
    for _ in range(3):
        engine.assess(signal(), snapshot(50.0), market(spread=0.01), instrument)
    assert engine.state.reject_counts[ReasonCode.SPREAD_TOO_WIDE.value] == 3
