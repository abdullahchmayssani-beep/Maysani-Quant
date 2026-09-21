"""Execution realism tests (Sections 13.2, 21.5, 21.9)."""
from __future__ import annotations

import pytest

from maysani_quant.domain.enums import Action, AmbiguousBarPolicy, Side, Verdict
from maysani_quant.domain.models import InstrumentSpec, Position, RiskDecision
from maysani_quant.execution.costs import CostConfig, CostModel
from maysani_quant.execution.simulator import ExecutionSimulator
from tests.conftest import START, make_bar


def approving_decision(size: float = 100.0, stop: float = 0.004) -> RiskDecision:
    return RiskDecision(
        decision_id="risk-1",
        as_of=START,
        verdict=Verdict.APPROVE,
        approved_size=size,
        requested_size=size,
        stop_distance=stop,
        risk_config_version="risk-test-v1",
    )


@pytest.mark.invariant
def test_fill_uses_next_bar_open_not_decision_bar_close(instrument, cost_model):
    """The decision bar's close is known to the strategy, so it may not be a fill price."""
    simulator = ExecutionSimulator(cost_model, instrument)
    decision_bar = make_bar(0, 1.1000, 1.1100, 1.0900, 1.1050)
    next_bar = make_bar(1, 1.1020, 1.1120, 1.0920, 1.1070)

    intent = simulator.build_intent(approving_decision(), Action.BUY, "EURUSD", START, "dec-1")
    fills = simulator.submit(intent, next_bar)

    assert len(fills) == 1
    assert fills[0].reference_price == next_bar.open
    assert fills[0].reference_price != decision_bar.close
    assert fills[0].price > next_bar.open, "a buy fills above the reference mid"


def test_zero_size_intent_is_rejected_not_filled(instrument, cost_model):
    simulator = ExecutionSimulator(cost_model, instrument)
    intent = simulator.build_intent(approving_decision(size=10.0), Action.BUY, "EURUSD", START, "d")
    object.__setattr__(intent, "size", 0.0)
    fills = simulator.submit(intent, make_bar(1, 1.1, 1.1, 1.1, 1.1))
    assert fills[0].status.value == "REJECTED"


@pytest.mark.invariant
def test_ambiguous_bar_resolves_adversely_for_a_long(instrument, cost_model):
    """Stop inside the bar range with unknown path -> assume the stop was hit."""
    simulator = ExecutionSimulator(cost_model, instrument, AmbiguousBarPolicy.ADVERSE)
    position = Position("EURUSD", Side.LONG, 100.0, 1.1000, START, stop_price=1.0950)
    # Bar dips to 1.0940 (through the stop) but closes higher at 1.1080.
    bar = make_bar(1, 1.1000, 1.1100, 1.0940, 1.1080)

    hit, price, note = simulator.resolve_stop(position, bar)
    assert hit is True
    assert price == pytest.approx(1.0950)
    assert "adverse" in note


@pytest.mark.invariant
def test_ambiguous_bar_can_be_skipped_but_never_resolved_favourably(instrument, cost_model):
    simulator = ExecutionSimulator(cost_model, instrument, AmbiguousBarPolicy.SKIP)
    position = Position("EURUSD", Side.LONG, 100.0, 1.1000, START, stop_price=1.0950)
    bar = make_bar(1, 1.1000, 1.1100, 1.0940, 1.1080)
    hit, price, note = simulator.resolve_stop(position, bar)
    assert hit is False
    assert note == "ambiguous_bar_skipped"


@pytest.mark.invariant
def test_gap_through_stop_fills_at_the_open_not_the_stop_level(instrument, cost_model):
    """The stop level is not a guaranteed price. A gap fills worse."""
    simulator = ExecutionSimulator(cost_model, instrument)
    position = Position("EURUSD", Side.LONG, 100.0, 1.1000, START, stop_price=1.0950)
    gapped = make_bar(1, 1.0800, 1.0850, 1.0750, 1.0820)   # opens far below the stop

    hit, price, note = simulator.resolve_stop(position, gapped)
    assert hit is True
    assert price < 1.0950, "a gap must not be filled at the stop level"
    assert note == "gap_through_stop_at_open"


def test_short_stop_uses_the_ask_side(instrument, cost_model):
    simulator = ExecutionSimulator(cost_model, instrument)
    position = Position("EURUSD", Side.SHORT, 100.0, 1.1000, START, stop_price=1.1050)
    bar = make_bar(1, 1.1000, 1.1060, 1.0990, 1.1010)
    hit, price, _ = simulator.resolve_stop(position, bar)
    assert hit is True
    assert price == pytest.approx(1.1050)


def test_no_stop_means_no_stop_event(instrument, cost_model):
    simulator = ExecutionSimulator(cost_model, instrument)
    position = Position("EURUSD", Side.LONG, 100.0, 1.1000, START, stop_price=None)
    hit, _, _ = simulator.resolve_stop(position, make_bar(1, 1.0, 1.0, 0.5, 0.8))
    assert hit is False


@pytest.mark.invariant
def test_dataset_spread_model_refuses_to_guess(instrument):
    """spread_model='dataset' with no bid/ask must fail loudly, not fall back."""
    model = CostModel(CostConfig(spread_model="dataset"))
    with pytest.raises(ValueError, match="no spread"):
        model.spread_for(None)


def test_dataset_spread_model_uses_the_bar_spread(instrument):
    model = CostModel(CostConfig(spread_model="dataset"))
    assert model.spread_for(0.00031) == pytest.approx(0.00031)


def test_commission_minimum_is_applied(instrument):
    model = CostModel(CostConfig(commission_per_unit=0.00001, commission_minimum=0.05))
    assert model.commission(10.0) == pytest.approx(0.05)
    assert model.commission(100000.0) == pytest.approx(1.0)


def test_financing_hook_defaults_to_zero_and_scales_with_days(instrument):
    model = CostModel(CostConfig())
    assert model.financing(100.0, True, 3.0) == 0.0
    charged = CostModel(CostConfig(financing_per_unit_per_day_long=0.0001))
    assert charged.financing(100.0, True, 3.0) == pytest.approx(0.03)


def test_size_rounds_down_to_the_tradable_step():
    instrument = InstrumentSpec("EURUSD", "EUR", "USD", size_step=1000.0, min_order_size=1000.0)
    assert instrument.round_size_down(1999.9) == 1000.0
    assert instrument.round_size_down(999.0) == 0.0
