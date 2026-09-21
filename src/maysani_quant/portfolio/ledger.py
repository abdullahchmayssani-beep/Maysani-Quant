"""Portfolio ledger and accounting model.

Accounting identity enforced after every event (Section 21.9):

    equity = cash + unrealized_pnl

where `cash` already carries every realized P&L, commission, spread cost,
slippage cost and financing charge that has occurred, and `unrealized_pnl` is
marked at the price we could *exit* at (bid for a long, ask for a short), not
at the midpoint. Marking at mid would show an unrealized profit that cannot be
realized, which is a small lie that compounds into a large one.

Single instrument, single position in V0.1. The interfaces are written against
an aggregate so the accounting does not have to be rewritten for a book.
"""
from __future__ import annotations

from datetime import datetime

from maysani_quant.domain.enums import Action, OrganismState, Side
from maysani_quant.domain.models import (
    Fill,
    InstrumentSpec,
    PortfolioSnapshot,
    Position,
)


class AccountingError(RuntimeError):
    """The identity above failed to hold. Always a bug, never a market event."""


class PortfolioLedger:
    def __init__(
        self,
        initial_equity: float,
        instrument: InstrumentSpec,
        death_threshold: float = 0.0,
        margin_requirement_pct: float = 0.20,
        tolerance: float = 1e-9,
    ) -> None:
        self.instrument = instrument
        self.initial_equity = initial_equity
        self.cash = initial_equity
        self.death_threshold = death_threshold
        self.margin_requirement_pct = margin_requirement_pct
        self.tolerance = tolerance

        self.position: Position | None = None
        self.peak_equity = initial_equity
        self.realized_pnl_cum = 0.0
        self.cost_paid_cum = 0.0
        self.financing_paid_cum = 0.0
        # spread + slippage are priced INTO fills, so they must not be
        # subtracted from cash a second time during reconciliation
        self._embedded_costs = 0.0
        self.state = OrganismState.ALIVE
        self.last_mark_price = 0.0
        self.closed_trade_pnls: list[float] = []
        self._last_realized = 0.0

    # --------------------------------------------------------------- marking
    def exit_price(self, mid: float, spread: float, side: Side) -> float:
        half = spread / 2.0
        return mid - half if side is Side.LONG else mid + half

    def unrealized(self, mid: float, spread: float) -> float:
        if self.position is None:
            return 0.0
        px = self.exit_price(mid, spread, self.position.side)
        delta = px - self.position.average_price
        return self.position.signed_units * delta * self.instrument.contract_multiplier

    def equity(self, mid: float, spread: float) -> float:
        return self.cash + self.unrealized(mid, spread)

    # ----------------------------------------------------------------- fills
    def apply_fill(self, fill: Fill) -> float:
        """Apply a fill. Returns realized P&L from this fill (0.0 on an open).

        Costs hit cash immediately and are never netted into the entry price,
        so cost drag stays visible in the report instead of hiding inside a
        flattering average price.
        """
        realized = 0.0
        self.cash -= fill.commission
        self.cost_paid_cum += fill.total_cost
        self.record_embedded_cost(fill.spread_cost + fill.slippage_cost)

        if self.position is None:
            side = Side.LONG if fill.action is Action.BUY else Side.SHORT
            self.position = Position(
                instrument=fill.instrument,
                side=side,
                units=fill.size,
                average_price=fill.price,
                opened_at=fill.timestamp,
            )
        else:
            pos = self.position
            closing = (pos.side is Side.LONG and fill.action is Action.SELL) or (
                pos.side is Side.SHORT and fill.action is Action.BUY
            )
            if not closing:
                # V0.1 does not scale into positions; the risk engine's cluster
                # gate blocks it upstream. Reaching here is a bug, not a trade.
                raise AccountingError(
                    "attempt to increase an existing position; V0.1 allows one position"
                )
            if fill.size > pos.units + self.tolerance:
                raise AccountingError(
                    f"close size {fill.size} exceeds position {pos.units}"
                )
            delta = fill.price - pos.average_price
            direction = 1.0 if pos.side is Side.LONG else -1.0
            realized = direction * delta * fill.size * self.instrument.contract_multiplier
            self.cash += realized
            self.realized_pnl_cum += realized
            remaining = pos.units - fill.size
            if remaining <= self.tolerance:
                self.closed_trade_pnls.append(realized)
                self.position = None
            else:
                self.position = Position(
                    instrument=pos.instrument,
                    side=pos.side,
                    units=remaining,
                    average_price=pos.average_price,
                    opened_at=pos.opened_at,
                    stop_price=pos.stop_price,
                    financing_paid=pos.financing_paid,
                )
        self._last_realized = realized
        return realized

    def set_stop(self, stop_price: float | None) -> None:
        if self.position is None:
            return
        pos = self.position
        self.position = Position(
            instrument=pos.instrument,
            side=pos.side,
            units=pos.units,
            average_price=pos.average_price,
            opened_at=pos.opened_at,
            stop_price=stop_price,
            financing_paid=pos.financing_paid,
        )

    def apply_financing(self, amount: float) -> None:
        """Positive amount = cost charged to the account."""
        if amount == 0.0 or self.position is None:
            return
        self.cash -= amount
        self.cost_paid_cum += amount
        self.financing_paid_cum += amount
        pos = self.position
        self.position = Position(
            instrument=pos.instrument,
            side=pos.side,
            units=pos.units,
            average_price=pos.average_price,
            opened_at=pos.opened_at,
            stop_price=pos.stop_price,
            financing_paid=pos.financing_paid + amount,
        )

    # ------------------------------------------------------------- snapshots
    def mark(self, timestamp: datetime, mid: float, spread: float) -> PortfolioSnapshot:
        self.last_mark_price = mid
        unrealized = self.unrealized(mid, spread)
        equity = self.cash + unrealized
        self.peak_equity = max(self.peak_equity, equity)
        drawdown = 0.0 if self.peak_equity <= 0 else max(0.0, 1.0 - equity / self.peak_equity)

        if self.state is OrganismState.ALIVE and equity <= self.death_threshold:
            self.state = OrganismState.DEAD

        units = 0.0 if self.position is None else self.position.signed_units
        gross = abs(units) * mid * self.instrument.contract_multiplier
        net = units * mid * self.instrument.contract_multiplier
        leverage = 0.0 if equity <= 0 else gross / equity
        margin_used = gross * self.margin_requirement_pct

        snapshot = PortfolioSnapshot(
            timestamp=timestamp,
            cash=self.cash,
            unrealized_pnl=unrealized,
            equity=equity,
            gross_notional=gross,
            net_notional=net,
            leverage=leverage,
            margin_used=margin_used,
            margin_free=max(0.0, equity - margin_used),
            peak_equity=self.peak_equity,
            drawdown=drawdown,
            state=self.state,
            position=self.position,
            realized_pnl_cum=self.realized_pnl_cum,
            cost_paid_cum=self.cost_paid_cum,
        )
        self.reconcile(snapshot)
        return snapshot

    def reconcile(self, snapshot: PortfolioSnapshot) -> None:
        expected = snapshot.cash + snapshot.unrealized_pnl
        if abs(expected - snapshot.equity) > 1e-6:
            raise AccountingError(
                f"equity identity violated at {snapshot.timestamp}: "
                f"cash={snapshot.cash} unrealized={snapshot.unrealized_pnl} "
                f"equity={snapshot.equity}"
            )
        expected_cash = (
            self.initial_equity + self.realized_pnl_cum - self._non_pnl_costs()
        )
        if abs(expected_cash - snapshot.cash) > 1e-6:
            raise AccountingError(
                f"cash identity violated at {snapshot.timestamp}: "
                f"expected={expected_cash} actual={snapshot.cash}"
            )

    def _non_pnl_costs(self) -> float:
        """Costs that left the account as cash: commissions and financing.

        Spread and slippage are already embedded in fill prices, so they show up
        through realized P&L and must NOT be subtracted twice here.
        """
        return self.cost_paid_cum - self._embedded_costs

    def record_embedded_cost(self, amount: float) -> None:
        self._embedded_costs += amount

    def to_state(self) -> dict:
        """Serialisable ledger state for restart/persistence tests."""
        pos = self.position
        return {
            "cash": self.cash,
            "initial_equity": self.initial_equity,
            "peak_equity": self.peak_equity,
            "realized_pnl_cum": self.realized_pnl_cum,
            "cost_paid_cum": self.cost_paid_cum,
            "embedded_costs": self._embedded_costs,
            "financing_paid_cum": self.financing_paid_cum,
            "state": self.state.value,
            "closed_trade_pnls": list(self.closed_trade_pnls),
            "position": None
            if pos is None
            else {
                "instrument": pos.instrument,
                "side": pos.side.value,
                "units": pos.units,
                "average_price": pos.average_price,
                "opened_at": pos.opened_at.isoformat(),
                "stop_price": pos.stop_price,
                "financing_paid": pos.financing_paid,
            },
        }

    def load_state(self, payload: dict) -> None:
        self.cash = float(payload["cash"])
        self.initial_equity = float(payload["initial_equity"])
        self.peak_equity = float(payload["peak_equity"])
        self.realized_pnl_cum = float(payload["realized_pnl_cum"])
        self.cost_paid_cum = float(payload["cost_paid_cum"])
        self._embedded_costs = float(payload.get("embedded_costs", 0.0))
        self.financing_paid_cum = float(payload.get("financing_paid_cum", 0.0))
        self.state = OrganismState(payload["state"])
        self.closed_trade_pnls = list(payload.get("closed_trade_pnls", []))
        pos = payload.get("position")
        if pos is None:
            self.position = None
        else:
            self.position = Position(
                instrument=pos["instrument"],
                side=Side(pos["side"]),
                units=float(pos["units"]),
                average_price=float(pos["average_price"]),
                opened_at=datetime.fromisoformat(pos["opened_at"]),
                stop_price=pos.get("stop_price"),
                financing_paid=float(pos.get("financing_paid", 0.0)),
            )
