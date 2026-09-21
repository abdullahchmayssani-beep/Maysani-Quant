"""Risk layer contract (Section 12).

The risk engine is a pure function of (signal, portfolio, market state, config).
It holds no reference to the execution layer, cannot be passed a callback, and
returns a decision object rather than performing an action. That asymmetry is
the whole point: a REJECT is data, and the only component that can turn a
decision into an order is `execution.simulator`, which refuses non-approving
decisions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from maysani_quant.domain.models import (
    InstrumentSpec,
    PortfolioSnapshot,
    RiskDecision,
    Signal,
)


@dataclass(frozen=True)
class MarketState:
    """What risk knows about conditions at decision time. No prices from the future."""

    as_of: datetime
    instrument: str
    reference_price: float
    spread: float
    atr: float | None
    realized_vol: float | None
    staleness_bars: float
    data_quality_ok: bool
    system_healthy: bool = True
    in_event_window: bool = False


@dataclass(frozen=True)
class RiskConfig:
    """Every number here is provisional and lives in config, never in code paths.

    Defaults are placeholders chosen to be restrictive, not optimal. Section 12:
    "The first goal is to prove constraint correctness, not optimize the risk
    percentage."
    """

    config_version: str = "risk-v0.1.0"
    risk_per_trade_pct: float = 0.01
    max_leverage: float = 5.0
    margin_requirement_pct: float = 0.20
    max_margin_utilisation: float = 0.50
    max_open_risk_pct: float = 0.02
    daily_loss_limit_pct: float = 0.03
    max_drawdown_pct: float = 0.20
    drawdown_throttle: tuple[tuple[float, float], ...] = (
        (0.05, 1.0),
        (0.10, 0.50),
        (0.15, 0.25),
    )
    max_spread_price: float = 0.0005
    max_realized_vol: float = 0.05
    vol_target: float | None = None
    max_staleness_bars: float = 2.0
    min_stop_distance_price: float = 0.0001
    max_stop_distance_price: float = 0.05
    event_window_blocks_entry: bool = True

    def throttle_multiplier(self, drawdown: float) -> tuple[float, bool]:
        """Return (multiplier, was_throttled) for the current drawdown depth."""
        multiplier = 1.0
        throttled = False
        for threshold, mult in sorted(self.drawdown_throttle):
            if drawdown >= threshold:
                multiplier = mult
                throttled = True
        return multiplier, throttled


@dataclass
class RiskState:
    """Mutable session state that must survive a restart (Section 12 invariants)."""

    session_date: str | None = None
    session_start_equity: float = 0.0
    realized_loss_today: float = 0.0
    peak_equity: float = 0.0
    kill_switch: bool = False
    decisions_emitted: int = 0
    reject_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "session_date": self.session_date,
            "session_start_equity": self.session_start_equity,
            "realized_loss_today": self.realized_loss_today,
            "peak_equity": self.peak_equity,
            "kill_switch": self.kill_switch,
            "decisions_emitted": self.decisions_emitted,
            "reject_counts": dict(self.reject_counts),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> RiskState:
        return cls(
            session_date=payload.get("session_date"),
            session_start_equity=float(payload.get("session_start_equity", 0.0)),
            realized_loss_today=float(payload.get("realized_loss_today", 0.0)),
            peak_equity=float(payload.get("peak_equity", 0.0)),
            kill_switch=bool(payload.get("kill_switch", False)),
            decisions_emitted=int(payload.get("decisions_emitted", 0)),
            reject_counts=dict(payload.get("reject_counts", {})),
        )


class RiskPolicy(Protocol):
    config_version: str

    def assess(
        self,
        signal: Signal,
        portfolio: PortfolioSnapshot,
        market: MarketState,
        instrument: InstrumentSpec,
    ) -> RiskDecision:  # pragma: no cover - protocol
        ...
