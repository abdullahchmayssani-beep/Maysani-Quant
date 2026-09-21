"""Closed vocabularies. Reason codes are machine-readable by contract (Section 12)."""
from __future__ import annotations

from enum import Enum


class Action(str, Enum):
    """WAIT is a first-class action, not a failure to decide."""

    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class OrderType(str, Enum):
    MARKET = "MARKET"


class FillStatus(str, Enum):
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    UNKNOWN = "UNKNOWN"


class Verdict(str, Enum):
    APPROVE = "APPROVE"
    APPROVE_WITH_REDUCED_SIZE = "APPROVE_WITH_REDUCED_SIZE"
    REJECT = "REJECT"


class OrganismState(str, Enum):
    ALIVE = "ALIVE"
    DEAD = "DEAD"


class AmbiguousBarPolicy(str, Enum):
    """Section 13.2: never resolve an unknown intrabar path in our own favour."""

    ADVERSE = "adverse"
    SKIP = "skip"


class QualityFlag(str, Enum):
    OK = "OK"
    GAP = "GAP"
    DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    INCONSISTENT_OHLC = "INCONSISTENT_OHLC"
    NEGATIVE_SPREAD = "NEGATIVE_SPREAD"
    SYNTHETIC = "SYNTHETIC"
    # V0.2 additions (ADR 0003) - canonical-validation-only flags. Never
    # produced by data/validation.py's V0.1 validate_bars.
    NON_FINITE = "NON_FINITE"
    NON_POSITIVE_PRICE = "NON_POSITIVE_PRICE"
    TIMEZONE_NAIVE = "TIMEZONE_NAIVE"
    WEEKEND_GAP = "WEEKEND_GAP"
    SUSPICIOUS_GAP = "SUSPICIOUS_GAP"


class QualitySeverity(str, Enum):
    """Deterministic severity for a canonical-validation issue (ADR 0003).

    Ordinal order matters: dataset severity is the max seen. An INVALID
    dataset must not silently enter a backtest.
    """

    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"

    @property
    def rank(self) -> int:
        return {"VALID": 0, "WARNING": 1, "INVALID": 2}[self.value]


class ReasonCode(str, Enum):
    OK = "OK"
    # data / system gates
    DATA_STALE = "DATA_STALE"
    DATA_QUALITY_FAIL = "DATA_QUALITY_FAIL"
    FEATURES_UNAVAILABLE = "FEATURES_UNAVAILABLE"
    SYSTEM_UNHEALTHY = "SYSTEM_UNHEALTHY"
    # organism / capital
    ORGANISM_DEAD = "ORGANISM_DEAD"
    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"
    EQUITY_NON_POSITIVE = "EQUITY_NON_POSITIVE"
    # sizing gates
    SIZE_BELOW_MIN = "SIZE_BELOW_MIN"
    SIZE_REDUCED_PER_TRADE_RISK = "SIZE_REDUCED_PER_TRADE_RISK"
    SIZE_REDUCED_LEVERAGE = "SIZE_REDUCED_LEVERAGE"
    SIZE_REDUCED_MARGIN = "SIZE_REDUCED_MARGIN"
    SIZE_REDUCED_MAX_OPEN_RISK = "SIZE_REDUCED_MAX_OPEN_RISK"
    SIZE_REDUCED_DRAWDOWN_THROTTLE = "SIZE_REDUCED_DRAWDOWN_THROTTLE"
    SIZE_REDUCED_VOLATILITY = "SIZE_REDUCED_VOLATILITY"
    # blocking gates
    DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"
    MAX_DRAWDOWN = "MAX_DRAWDOWN"
    SPREAD_TOO_WIDE = "SPREAD_TOO_WIDE"
    VOLATILITY_UNSAFE = "VOLATILITY_UNSAFE"
    STOP_DISTANCE_INVALID = "STOP_DISTANCE_INVALID"
    EXPOSURE_LIMIT = "EXPOSURE_LIMIT"
    CORRELATION_CLUSTER_LIMIT = "CORRELATION_CLUSTER_LIMIT"
    EVENT_RISK_WINDOW = "EVENT_RISK_WINDOW"
    # strategy-side reason codes (proposals, not permissions)
    NO_SIGNAL = "NO_SIGNAL"
    WARMUP = "WARMUP"
    VOL_FILTER = "VOL_FILTER"
    ENTRY_LONG = "ENTRY_LONG"
    ENTRY_SHORT = "ENTRY_SHORT"
    EXIT_SIGNAL = "EXIT_SIGNAL"
    HOLD = "HOLD"
