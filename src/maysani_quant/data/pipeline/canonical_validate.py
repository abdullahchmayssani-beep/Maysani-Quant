"""CANONICAL VALIDATE: severity-aware checks on canonical `MarketBar`s only.

Deliberately a different module and a different report type from V0.1's
`data/validation.py::validate_bars` - that function keeps governing the CSV
path unchanged. This one adds FX-aware gap classification and a deterministic
VALID/WARNING/INVALID severity per ADR 0003 s.5-6. It never repairs a bar;
every check either records an issue or leaves the bar untouched.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from maysani_quant.domain.enums import QualityFlag, QualitySeverity
from maysani_quant.domain.models import MarketBar

_SEVERITY = {
    QualityFlag.OK: QualitySeverity.VALID,
    QualityFlag.SYNTHETIC: QualitySeverity.VALID,
    QualityFlag.WEEKEND_GAP: QualitySeverity.VALID,
    QualityFlag.SUSPICIOUS_GAP: QualitySeverity.WARNING,
    QualityFlag.GAP: QualitySeverity.WARNING,
    QualityFlag.DUPLICATE_TIMESTAMP: QualitySeverity.INVALID,
    QualityFlag.OUT_OF_ORDER: QualitySeverity.INVALID,
    QualityFlag.INCONSISTENT_OHLC: QualitySeverity.INVALID,
    QualityFlag.NEGATIVE_SPREAD: QualitySeverity.INVALID,
    QualityFlag.NON_FINITE: QualitySeverity.INVALID,
    QualityFlag.NON_POSITIVE_PRICE: QualitySeverity.INVALID,
    QualityFlag.TIMEZONE_NAIVE: QualitySeverity.INVALID,
}

# Fixed heuristic, not a trading calendar - see ADR 0003 s.6.
_WEEKEND_CAP = timedelta(days=3)
_WEEKEND_CLOSE_HOUR_UTC = 21
# A weekend gap must end at the reopen, not merely begin at the close. The
# tolerance absorbs the hour of DST drift in the real (New York anchored)
# session boundary plus a thin first-tick lag; anything later is a data hole
# that happens to start on a weekend, not a weekend.
_WEEKEND_REOPEN_TOLERANCE = timedelta(hours=6)


def _in_weekend_closure(dt: datetime) -> bool:
    """Fri 21:00 UTC through Sun 21:00 UTC, the common interbank FX
    convention. No holiday calendar, no broker session table, and no DST
    handling - the real boundary is 17:00 New York, which is 21:00 UTC only
    in EDT and 22:00 UTC in EST (documented limitation, ADR 0003 s.6)."""
    weekday, hour = dt.weekday(), dt.hour  # Mon=0 ... Sun=6
    if weekday == 4 and hour >= _WEEKEND_CLOSE_HOUR_UTC:
        return True
    if weekday == 5:
        return True
    if weekday == 6 and hour < _WEEKEND_CLOSE_HOUR_UTC:
        return True
    return False


def _weekend_reopen_after(dt: datetime) -> datetime:
    """The first Sunday 21:00 UTC at or after `dt` - when the closure that
    contains `dt` is expected to end."""
    days_ahead = (6 - dt.weekday()) % 7
    reopen = (dt + timedelta(days=days_ahead)).replace(
        hour=_WEEKEND_CLOSE_HOUR_UTC, minute=0, second=0, microsecond=0
    )
    return reopen if reopen >= dt else reopen + timedelta(days=7)


@dataclass(frozen=True)
class CanonicalIssue:
    timestamp: datetime
    flag: QualityFlag
    severity: QualitySeverity
    detail: str


@dataclass
class CanonicalValidationReport:
    bar_count: int
    first_time: datetime | None
    last_time: datetime | None
    issues: list[CanonicalIssue] = field(default_factory=list)

    @property
    def severity(self) -> QualitySeverity:
        if not self.issues:
            return QualitySeverity.VALID
        return max((i.severity for i in self.issues), key=lambda s: s.rank)

    @property
    def ok(self) -> bool:
        """An INVALID dataset must not silently enter a backtest."""
        return self.severity is not QualitySeverity.INVALID

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for issue in self.issues:
            out[issue.flag.value] = out.get(issue.flag.value, 0) + 1
        return out

    def summary(self) -> str:
        if not self.issues:
            return f"{self.bar_count} bars, no issues ({self.severity.value})"
        parts = ", ".join(f"{k}={v}" for k, v in sorted(self.counts().items()))
        return f"{self.bar_count} bars, {self.severity.value}: {parts}"


def _finite_fields(bar: MarketBar) -> list[float]:
    values = [bar.open, bar.high, bar.low, bar.close]
    for optional in (bar.volume, bar.bid_close, bar.ask_close, bar.spread):
        if optional is not None:
            values.append(optional)
    return values


def validate_canonical_bars(
    bars: Sequence[MarketBar],
    *,
    expected_bar_seconds: int,
    require_bid_ask: bool = False,
) -> CanonicalValidationReport:
    report = CanonicalValidationReport(
        bar_count=len(bars),
        first_time=bars[0].end_time if bars else None,
        last_time=bars[-1].end_time if bars else None,
    )

    def add(ts: datetime, flag: QualityFlag, detail: str) -> None:
        report.issues.append(CanonicalIssue(ts, flag, _SEVERITY[flag], detail))

    seen: set[datetime] = set()
    prev: MarketBar | None = None
    for bar in bars:
        if bar.start_time.tzinfo is None or bar.end_time.tzinfo is None or bar.available_time.tzinfo is None:
            add(bar.end_time, QualityFlag.TIMEZONE_NAIVE, "naive timestamp on a canonical bar")

        if not all(math.isfinite(v) for v in _finite_fields(bar)):
            add(bar.end_time, QualityFlag.NON_FINITE, "non-finite price/volume field")

        if require_bid_ask and (bar.bid_close is None or bar.ask_close is None or bar.spread is None):
            add(bar.end_time, QualityFlag.NON_FINITE, "bid/ask fidelity required but missing")

        # A spot FX price is never zero or negative. Nothing else in this
        # function catches it: a uniformly negative bar is finite, internally
        # OHLC-consistent and has a positive ask-bid spread, so without this
        # check a misparsed artifact could pass as VALID.
        prices = [bar.open, bar.high, bar.low, bar.close]
        prices += [p for p in (bar.bid_close, bar.ask_close) if p is not None]
        if any(p <= 0 for p in prices if math.isfinite(p)):
            add(
                bar.end_time,
                QualityFlag.NON_POSITIVE_PRICE,
                f"non-positive price in {prices}",
            )

        hi = max(bar.open, bar.close)
        lo = min(bar.open, bar.close)
        if bar.high < hi or bar.low > lo or bar.high < bar.low:
            add(
                bar.end_time,
                QualityFlag.INCONSISTENT_OHLC,
                f"O={bar.open} H={bar.high} L={bar.low} C={bar.close}",
            )

        if bar.spread is not None and bar.spread < 0:
            add(bar.end_time, QualityFlag.NEGATIVE_SPREAD, f"spread={bar.spread}")
        if bar.bid_close is not None and bar.ask_close is not None and bar.ask_close < bar.bid_close:
            add(
                bar.end_time,
                QualityFlag.NEGATIVE_SPREAD,
                f"ask={bar.ask_close} < bid={bar.bid_close}",
            )

        if bar.end_time in seen:
            add(bar.end_time, QualityFlag.DUPLICATE_TIMESTAMP, "repeated end_time")
        seen.add(bar.end_time)

        if bar.available_time < bar.end_time:
            add(bar.end_time, QualityFlag.OUT_OF_ORDER, "available_time earlier than end_time")

        if prev is not None:
            if bar.end_time <= prev.end_time:
                add(bar.end_time, QualityFlag.OUT_OF_ORDER, "end_time not increasing")
            elif bar.start_time > prev.end_time:
                gap_seconds = (bar.start_time - prev.end_time).total_seconds()
                if gap_seconds >= expected_bar_seconds:
                    # A weekend gap must both START inside the closure and END
                    # at the reopen. Checking only the start let a multi-day
                    # mid-week hole that happened to begin on a Sunday pass as
                    # VALID and disappear from the report.
                    if (
                        _in_weekend_closure(prev.end_time)
                        and (bar.start_time - prev.end_time) <= _WEEKEND_CAP
                        and bar.start_time
                        <= _weekend_reopen_after(prev.end_time) + _WEEKEND_REOPEN_TOLERANCE
                    ):
                        add(
                            bar.end_time,
                            QualityFlag.WEEKEND_GAP,
                            f"{gap_seconds:.0f}s gap starting at weekend closure",
                        )
                    else:
                        add(
                            bar.end_time,
                            QualityFlag.SUSPICIOUS_GAP,
                            f"{gap_seconds:.0f}s gap, expected ~{expected_bar_seconds}s",
                        )
        prev = bar
    return report
