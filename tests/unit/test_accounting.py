"""Accounting invariants (Section 21.9).

The flat-price round trip is the single most important test in V0.1: on a
perfectly flat price series, a complete round trip must lose exactly the
modelled costs. If this passes, the engine cannot manufacture free money out of
its own execution model. If it fails, nothing downstream is worth reading.
"""
from __future__ import annotations

import pytest

from maysani_quant.domain.enums import Action, FillStatus
from maysani_quant.domain.models import Fill, InstrumentSpec
from maysani_quant.execution.costs import CostConfig, CostModel
from maysani_quant.portfolio.ledger import AccountingError, PortfolioLedger
from tests.conftest import START


def _fill(action: Action, price: float, size: float, spread_cost=0.0, slip=0.0, comm=0.0) -> Fill:
    return Fill(
        intent_id="t",
        timestamp=START,
        instrument="EURUSD",
        action=action,
        price=price,
        size=size,
        status=FillStatus.FILLED,
        reference_price=price,
        spread_cost=spread_cost,
        slippage_cost=slip,
        commission=comm,
    )


@pytest.mark.invariant
def test_flat_price_round_trip_loses_exactly_modelled_costs(instrument: InstrumentSpec):
    """Price never moves. Long 100 units in and out. Loss == spread + commission."""
    mid = 1.10
    spread = 0.0002
    commission_per_unit = 0.00005
    size = 100.0

    costs = CostModel(
        CostConfig(
            fixed_spread_price=spread,
            slippage_price=0.0,
            commission_per_unit=commission_per_unit,
            scenario_name="roundtrip",
        )
    )
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument)

    buy = costs.execution_price(Action.BUY, mid, size, None)
    ledger.apply_fill(
        _fill(Action.BUY, buy.price, size, buy.spread_cost, buy.slippage_cost, buy.commission)
    )
    sell = costs.execution_price(Action.SELL, mid, size, None)
    ledger.apply_fill(
        _fill(Action.SELL, sell.price, size, sell.spread_cost, sell.slippage_cost, sell.commission)
    )

    snapshot = ledger.mark(START, mid, spread)
    expected_loss = spread * size + commission_per_unit * size * 2
    actual_loss = 50.0 - snapshot.equity

    assert snapshot.position is None
    assert actual_loss == pytest.approx(expected_loss, abs=1e-9)
    assert actual_loss > 0, "a round trip on a flat price must never be profitable"


@pytest.mark.invariant
def test_short_round_trip_also_loses_costs(instrument: InstrumentSpec):
    mid, spread, size = 1.10, 0.0002, 100.0
    costs = CostModel(CostConfig(fixed_spread_price=spread, slippage_price=0.0))
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument)

    sell = costs.execution_price(Action.SELL, mid, size, None)
    ledger.apply_fill(_fill(Action.SELL, sell.price, size, sell.spread_cost))
    buy = costs.execution_price(Action.BUY, mid, size, None)
    ledger.apply_fill(_fill(Action.BUY, buy.price, size, buy.spread_cost))

    snapshot = ledger.mark(START, mid, spread)
    assert 50.0 - snapshot.equity == pytest.approx(spread * size, abs=1e-9)


@pytest.mark.invariant
def test_buy_uses_ask_and_sell_uses_bid(instrument: InstrumentSpec):
    """Executable side, not midpoint (Section 13.2)."""
    mid, spread, slip = 1.10, 0.0002, 0.00001
    costs = CostModel(CostConfig(fixed_spread_price=spread, slippage_price=slip))

    buy = costs.execution_price(Action.BUY, mid, 10, None)
    sell = costs.execution_price(Action.SELL, mid, 10, None)

    assert buy.price == pytest.approx(mid + spread / 2 + slip)
    assert sell.price == pytest.approx(mid - spread / 2 - slip)
    assert buy.price > mid > sell.price, "costs must always run against us"


@pytest.mark.invariant
def test_equity_identity_holds_after_every_event(instrument: InstrumentSpec):
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument)
    ledger.apply_fill(_fill(Action.BUY, 1.1000, 50.0, comm=0.01))
    snap = ledger.mark(START, 1.1050, 0.0002)
    assert snap.equity == pytest.approx(snap.cash + snap.unrealized_pnl)
    ledger.apply_fill(_fill(Action.SELL, 1.1040, 50.0, comm=0.01))
    snap2 = ledger.mark(START, 1.1050, 0.0002)
    assert snap2.equity == pytest.approx(snap2.cash)


@pytest.mark.invariant
def test_unrealized_pnl_is_marked_at_the_exit_price_not_mid(instrument: InstrumentSpec):
    """A long marked at mid would show profit it cannot realise."""
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument)
    ledger.apply_fill(_fill(Action.BUY, 1.1000, 100.0))
    spread = 0.0002
    snap = ledger.mark(START, 1.1000, spread)
    # exit price for a long is the bid = mid - spread/2, so we are down half a spread
    assert snap.unrealized_pnl == pytest.approx(-(spread / 2) * 100.0)


def test_financing_reduces_cash_and_is_tracked(instrument: InstrumentSpec):
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument)
    ledger.apply_fill(_fill(Action.BUY, 1.1000, 100.0))
    ledger.apply_financing(0.05)
    snap = ledger.mark(START, 1.1000, 0.0)
    assert ledger.financing_paid_cum == pytest.approx(0.05)
    assert snap.cash == pytest.approx(50.0 - 0.05)


def test_scaling_into_a_position_is_refused(instrument: InstrumentSpec):
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument)
    ledger.apply_fill(_fill(Action.BUY, 1.1000, 50.0))
    with pytest.raises(AccountingError):
        ledger.apply_fill(_fill(Action.BUY, 1.1000, 50.0))


def test_closing_more_than_held_is_refused(instrument: InstrumentSpec):
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument)
    ledger.apply_fill(_fill(Action.BUY, 1.1000, 50.0))
    with pytest.raises(AccountingError):
        ledger.apply_fill(_fill(Action.SELL, 1.1000, 80.0))


@pytest.mark.invariant
def test_death_state_is_terminal(instrument: InstrumentSpec):
    ledger = PortfolioLedger(initial_equity=50.0, instrument=instrument, death_threshold=45.0)
    ledger.apply_fill(_fill(Action.BUY, 1.1000, 1000.0))
    dead = ledger.mark(START, 1.0900, 0.0002)   # -10 USD on 1000 units
    assert dead.state.value == "DEAD"
    revived = ledger.mark(START, 1.2000, 0.0002)  # price recovers hard
    assert revived.state.value == "DEAD", "death must not be reversible by a price move"
