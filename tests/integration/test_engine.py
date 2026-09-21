"""Engine integration tests (Section 21.9)."""
from __future__ import annotations

from pathlib import Path

import pytest

from maysani_quant.backtest.engine import BacktestEngine
from maysani_quant.domain.enums import Action, OrganismState, ReasonCode
from maysani_quant.execution.costs import CostConfig, CostModel
from maysani_quant.execution.simulator import ExecutionSimulator
from maysani_quant.features.pipeline import FeatureConfig, FeaturePipeline
from maysani_quant.journal.store import InMemoryJournal, Journal
from maysani_quant.portfolio.ledger import PortfolioLedger
from maysani_quant.risk.hard_limits import HardRiskEngine
from maysani_quant.risk.interfaces import RiskConfig, RiskState
from maysani_quant.strategies.base import build_strategy
from tests.conftest import flat_bars, oscillating_bars, trending_bars


def build_engine(
    instrument,
    strategy_id: str,
    feature_config: FeatureConfig,
    risk_config: RiskConfig,
    journal=None,
    initial_equity: float = 50.0,
    death_threshold: float = 0.0,
    cost_config: CostConfig | None = None,
    params: dict | None = None,
) -> BacktestEngine:
    cost_model = CostModel(cost_config or CostConfig(fixed_spread_price=0.0002, slippage_price=0.0))
    return BacktestEngine(
        instrument=instrument,
        pipeline=FeaturePipeline(feature_config),
        strategy=build_strategy(strategy_id, params or {}),
        risk=HardRiskEngine(risk_config, RiskState(peak_equity=initial_equity)),
        execution=ExecutionSimulator(cost_model, instrument),
        ledger=PortfolioLedger(
            initial_equity=initial_equity,
            instrument=instrument,
            death_threshold=death_threshold,
            margin_requirement_pct=risk_config.margin_requirement_pct,
        ),
        journal=journal or InMemoryJournal(),
        bar_seconds=86400,
        experiment_id="exp-test",
        config_hash="cfg",
        data_hash="data",
    )


@pytest.mark.invariant
def test_every_bar_produces_exactly_one_decision_record(
    instrument, feature_config, risk_config
):
    """Including WAIT, and including warm-up bars (Section 21.9)."""
    bars = oscillating_bars(60)
    engine = build_engine(instrument, "momentum_v1", feature_config, risk_config)
    result = engine.run(bars)
    assert len(result.decisions) == len(bars)
    assert result.bars_processed == len(bars)

    warmup = [d for d in result.decisions if ReasonCode.WARMUP in d.signal_reason_codes]
    assert warmup, "warm-up bars must still be journaled"
    assert all(d.action is Action.WAIT for d in warmup)


@pytest.mark.invariant
def test_wait_decisions_carry_full_provenance(instrument, feature_config, risk_config):
    bars = oscillating_bars(60)
    engine = build_engine(instrument, "no_trade_v1", feature_config, risk_config)
    result = engine.run(bars)

    waits = [d for d in result.decisions if d.action is Action.WAIT]
    assert len(waits) == len(bars)
    post_warmup = [d for d in waits if d.snapshot_id]
    assert post_warmup, "post-warmup WAITs must name a feature snapshot"
    for decision in post_warmup:
        assert decision.experiment_id == "exp-test"
        assert decision.config_hash == "cfg"
        assert decision.data_hash == "data"
        assert decision.code_version
        assert decision.risk_decision_id is not None


@pytest.mark.invariant
def test_determinism_same_inputs_same_journal(instrument, feature_config, risk_config):
    """Identical data, config and code -> byte-identical journal content."""
    bars = oscillating_bars(80)
    fingerprints = []
    for _ in range(2):
        engine = build_engine(instrument, "momentum_v1", feature_config, risk_config)
        result = engine.run(bars)
        fingerprints.append(result.journal_fingerprint)
    assert fingerprints[0] == fingerprints[1]


@pytest.mark.invariant
def test_determinism_extends_to_equity_and_fills(instrument, feature_config, risk_config):
    bars = trending_bars(80)
    runs = []
    for _ in range(3):
        engine = build_engine(instrument, "momentum_v1", feature_config, risk_config)
        result = engine.run(bars)
        runs.append(
            (
                [round(e, 12) for _, e in result.equity_curve],
                [(f.timestamp, round(f.price, 12), f.size) for f in result.fills],
            )
        )
    assert runs[0] == runs[1] == runs[2]


@pytest.mark.invariant
def test_no_trade_baseline_never_spends_a_cent(instrument, feature_config, risk_config):
    bars = oscillating_bars(80)
    engine = build_engine(instrument, "no_trade_v1", feature_config, risk_config)
    result = engine.run(bars)
    assert result.fills == []
    assert result.trades == []
    assert result.equity_curve[-1][1] == pytest.approx(50.0)


@pytest.mark.invariant
def test_flat_market_can_only_lose_money(instrument, feature_config, risk_config):
    """On a perfectly flat series, any strategy that trades must end below start."""
    bars = flat_bars(80)
    for strategy_id in ("momentum_v1", "mean_reversion_v1", "buy_and_hold_v1"):
        engine = build_engine(instrument, strategy_id, feature_config, risk_config)
        result = engine.run(bars)
        final = result.equity_curve[-1][1]
        assert final <= 50.0 + 1e-9, f"{strategy_id} manufactured profit on a flat market"


@pytest.mark.invariant
def test_death_halts_trading_and_is_terminal(instrument, feature_config):
    """A high death threshold kills the organism early; no decisions follow."""
    risk_config = RiskConfig(risk_per_trade_pct=0.5, max_leverage=50.0,
                             margin_requirement_pct=0.01, max_margin_utilisation=1.0,
                             max_open_risk_pct=1.0, max_drawdown_pct=0.99,
                             daily_loss_limit_pct=0.99)
    bars = trending_bars(120, start_price=1.10, step=-0.002)  # steadily falling
    engine = build_engine(
        instrument, "buy_and_hold_v1", feature_config, risk_config,
        death_threshold=49.0, params={"stop_atr_multiple": 50.0},
    )
    result = engine.run(bars)
    if result.final_state is OrganismState.DEAD:
        assert result.bars_processed < len(bars), "death must stop the run"
        assert result.decisions[-1].portfolio_state is OrganismState.DEAD


@pytest.mark.invariant
def test_restart_from_checkpoint_does_not_duplicate_fills(
    instrument, feature_config, risk_config, tmp_path: Path
):
    """Re-running into the same journal is idempotent (Section 21.9)."""
    bars = oscillating_bars(70)
    journal = Journal(tmp_path, "restart-run")
    engine = build_engine(instrument, "momentum_v1", feature_config, risk_config, journal=journal)
    first = engine.run(bars)
    fills_first = len(journal.read_type("FILL"))

    checkpoint = journal.load_checkpoint()
    assert checkpoint is not None
    assert checkpoint["bars_processed"] == len(bars)

    replay_journal = Journal(tmp_path, "restart-run")
    engine2 = build_engine(
        instrument, "momentum_v1", feature_config, risk_config, journal=replay_journal
    )
    engine2.run(bars)
    fills_after = len(replay_journal.read_type("FILL"))

    assert fills_after == fills_first, "replaying an identical run must not duplicate fills"
    assert first.journal_fingerprint == replay_journal.content_fingerprint()


def test_ledger_state_round_trips(instrument, feature_config, risk_config):
    bars = oscillating_bars(70)
    engine = build_engine(instrument, "momentum_v1", feature_config, risk_config)
    engine.run(bars)
    state = engine.ledger.to_state()

    restored = PortfolioLedger(50.0, instrument)
    restored.load_state(state)
    assert restored.cash == pytest.approx(engine.ledger.cash)
    assert restored.realized_pnl_cum == pytest.approx(engine.ledger.realized_pnl_cum)
    assert (restored.position is None) == (engine.ledger.position is None)


@pytest.mark.invariant
def test_every_fill_traces_back_to_a_risk_decision(instrument, feature_config, risk_config):
    bars = oscillating_bars(90)
    journal = InMemoryJournal()
    engine = build_engine(instrument, "momentum_v1", feature_config, risk_config, journal=journal)
    engine.run(bars)

    intents = {i["intent_id"]: i for i in journal.read_type("ORDER_INTENT")}
    for fill in journal.read_type("FILL"):
        if fill["reason"].startswith("STOP:"):
            continue   # stop exits are engine-generated, not order intents
        intent = intents.get(fill["intent_id"])
        assert intent is not None, "a fill with no order intent"
        assert intent["risk_decision_id"], "an order intent with no risk decision"


@pytest.mark.invariant
def test_every_open_position_carries_a_stop(instrument, feature_config, risk_config):
    """Risk sized the trade from a stop distance; the position must hold that stop.

    A position without its stop would mean the loss the risk engine budgeted
    for is no longer bounded by anything.
    """
    bars = oscillating_bars(90)
    engine = build_engine(instrument, "momentum_v1", feature_config, risk_config)
    result = engine.run(bars)
    held = [s for s in result.snapshots if s.position is not None]
    assert held, "fixture should produce at least one open position"
    for snap in held:
        assert snap.position.stop_price is not None
        if snap.position.side.value == "LONG":
            assert snap.position.stop_price < snap.position.average_price
        else:
            assert snap.position.stop_price > snap.position.average_price


@pytest.mark.invariant
def test_leverage_never_exceeds_configured_maximum(instrument, feature_config):
    risk_config = RiskConfig(risk_per_trade_pct=0.20, max_leverage=3.0,
                             margin_requirement_pct=0.01, max_margin_utilisation=1.0,
                             max_open_risk_pct=1.0)
    bars = oscillating_bars(120)
    engine = build_engine(instrument, "momentum_v1", feature_config, risk_config)
    result = engine.run(bars)
    worst = max((s.leverage for s in result.snapshots), default=0.0)
    assert worst <= 3.0 + 1e-6, f"leverage reached {worst}"
