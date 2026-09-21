"""Domain models (Section 21.3).

Every record is frozen. Traceability is by explicit ID fields, not by object
identity: a DecisionRecord names the FeatureSnapshot, the Signal, the
RiskDecision and the PortfolioSnapshot it was produced from, so a run can be
reconstructed from the journal alone.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Mapping, Sequence

from maysani_quant.domain.enums import (
    Action,
    FillStatus,
    OrderType,
    OrganismState,
    QualityFlag,
    ReasonCode,
    Side,
    Verdict,
)


def to_jsonable(obj: Any) -> Any:
    """Recursively convert dataclasses/enums/datetimes into JSON-safe values."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (Action, Side, OrderType, FillStatus, Verdict, OrganismState, QualityFlag, ReasonCode)):
        return obj.value
    if isinstance(obj, Mapping):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]
    return obj


def stable_hash(payload: Any) -> str:
    """Deterministic SHA-256 of any JSON-able payload. Used for config/data hashes."""
    blob = json.dumps(to_jsonable(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class InstrumentSpec:
    """Broker/instrument metadata. Precision and minimum size are risk-relevant."""

    symbol: str
    base_currency: str
    quote_currency: str
    price_precision: int = 5
    size_step: float = 1.0
    min_order_size: float = 1.0
    contract_multiplier: float = 1.0

    def round_price(self, price: float) -> float:
        return round(price, self.price_precision)

    def round_size_down(self, size: float) -> float:
        """Always round size DOWN to the tradable step - never up into extra risk."""
        if self.size_step <= 0:
            return size
        steps = int(abs(size) / self.size_step + 1e-9)
        return steps * self.size_step


@dataclass(frozen=True)
class MarketBar:
    """One completed bar.

    `available_time` is when this row could have been known, and is the only
    timestamp the point-in-time view is allowed to filter on. `end_time` is
    event time. They are deliberately separate fields (Section 9.1).
    """

    instrument: str
    start_time: datetime
    end_time: datetime
    available_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    bid_close: float | None = None
    ask_close: float | None = None
    spread: float | None = None
    source: str = "unknown"
    quality_flags: tuple[QualityFlag, ...] = field(default_factory=tuple)

    @property
    def is_synthetic(self) -> bool:
        return QualityFlag.SYNTHETIC in self.quality_flags


@dataclass(frozen=True)
class FeatureSnapshot:
    """Features computed strictly from bars with available_time <= as_of."""

    snapshot_id: str
    as_of: datetime
    instrument: str
    values: Mapping[str, float]
    input_bar_count: int
    last_input_available_time: datetime
    code_version: str

    def get(self, name: str) -> float | None:
        value = self.values.get(name)
        if value is None:
            return None
        return float(value)


@dataclass(frozen=True)
class Signal:
    """A proposal. Carries no authority to size or execute anything."""

    as_of: datetime
    instrument: str
    strategy_id: str
    strategy_version: str
    action: Action
    score: float
    horizon_bars: int
    snapshot_id: str
    expected_return: float | None = None
    uncertainty: float | None = None
    stop_distance: float | None = None
    reason_codes: tuple[ReasonCode, ...] = field(default_factory=tuple)
    params_hash: str = ""


@dataclass(frozen=True)
class RiskDecision:
    """The only component that may authorise size. Reason codes are mandatory."""

    decision_id: str
    as_of: datetime
    verdict: Verdict
    approved_size: float
    requested_size: float
    stop_distance: float | None
    risk_config_version: str
    reason_codes: tuple[ReasonCode, ...] = field(default_factory=tuple)
    detail: Mapping[str, Any] = field(default_factory=dict)

    @property
    def permits_order(self) -> bool:
        return self.verdict is not Verdict.REJECT and self.approved_size > 0


@dataclass(frozen=True)
class OrderIntent:
    """Produced only from an approving RiskDecision (see execution.simulator)."""

    intent_id: str
    created_at: datetime
    instrument: str
    action: Action
    size: float
    order_type: OrderType
    decision_id: str
    risk_decision_id: str
    is_reducing: bool = False


@dataclass(frozen=True)
class Fill:
    intent_id: str
    timestamp: datetime
    instrument: str
    action: Action
    price: float
    size: float
    status: FillStatus
    reference_price: float
    spread_cost: float = 0.0
    slippage_cost: float = 0.0
    commission: float = 0.0
    reason: str = ""

    @property
    def total_cost(self) -> float:
        return self.spread_cost + self.slippage_cost + self.commission


@dataclass(frozen=True)
class Position:
    instrument: str
    side: Side
    units: float
    average_price: float
    opened_at: datetime
    stop_price: float | None = None
    financing_paid: float = 0.0

    @property
    def signed_units(self) -> float:
        return self.units if self.side is Side.LONG else -self.units


@dataclass(frozen=True)
class PortfolioSnapshot:
    timestamp: datetime
    cash: float
    unrealized_pnl: float
    equity: float
    gross_notional: float
    net_notional: float
    leverage: float
    margin_used: float
    margin_free: float
    peak_equity: float
    drawdown: float
    state: OrganismState
    position: Position | None = None
    realized_pnl_cum: float = 0.0
    cost_paid_cum: float = 0.0


@dataclass(frozen=True)
class DecisionRecord:
    """The audit spine: every bar produces one of these, including WAIT."""

    decision_id: str
    as_of: datetime
    instrument: str
    action: Action
    strategy_id: str
    strategy_version: str
    snapshot_id: str
    signal_score: float
    expected_costs: float
    risk_verdict: Verdict | None
    risk_decision_id: str | None
    risk_reason_codes: tuple[ReasonCode, ...]
    approved_size: float
    portfolio_equity: float
    portfolio_state: OrganismState
    experiment_id: str
    code_version: str
    config_hash: str
    data_hash: str
    signal_reason_codes: tuple[ReasonCode, ...] = field(default_factory=tuple)
    notes: str = ""


@dataclass(frozen=True)
class TradeRecord:
    trade_id: str
    instrument: str
    side: Side
    units: float
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    gross_pnl: float
    costs: float
    net_pnl: float
    financing: float
    duration_bars: int
    entry_decision_id: str
    exit_decision_id: str
    strategy_id: str
    exit_reason: str


@dataclass(frozen=True)
class ExperimentRecord:
    """Immutable trial record. Failed and abandoned trials stay in the registry."""

    experiment_id: str
    created_at: datetime
    hypothesis: str
    strategy_id: str
    strategy_version: str
    params: Mapping[str, Any]
    config_hash: str
    data_hash: str
    dataset_path: str
    code_version: str
    window_start: datetime | None
    window_end: datetime | None
    cost_model_hash: str
    risk_config_version: str
    status: str = "RUNNING"
    metrics: Mapping[str, Any] = field(default_factory=dict)
    parent_experiment_id: str | None = None
    notes: str = ""


def sequence_hash(items: Sequence[Any]) -> str:
    return stable_hash([to_jsonable(i) for i in items])
