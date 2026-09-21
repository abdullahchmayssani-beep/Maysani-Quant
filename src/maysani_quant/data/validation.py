"""Dataset validation.

Output feeds the risk engine's data-quality gate (Section 12). Validation does
not repair data: a silently "fixed" bar is an untraceable bar.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime

from maysani_quant.domain.enums import QualityFlag
from maysani_quant.domain.models import MarketBar


@dataclass
class ValidationIssue:
    timestamp: datetime
    flag: QualityFlag
    detail: str


@dataclass
class ValidationReport:
    bar_count: int
    first_time: datetime | None
    last_time: datetime | None
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(
            i.flag
            in (
                QualityFlag.DUPLICATE_TIMESTAMP,
                QualityFlag.OUT_OF_ORDER,
                QualityFlag.INCONSISTENT_OHLC,
                QualityFlag.NEGATIVE_SPREAD,
            )
            for i in self.issues
        )

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for issue in self.issues:
            out[issue.flag.value] = out.get(issue.flag.value, 0) + 1
        return out

    def summary(self) -> str:
        if not self.issues:
            return f"{self.bar_count} bars, no issues"
        parts = ", ".join(f"{k}={v}" for k, v in sorted(self.counts().items()))
        return f"{self.bar_count} bars, issues: {parts}"


def validate_bars(bars: Sequence[MarketBar]) -> ValidationReport:
    report = ValidationReport(
        bar_count=len(bars),
        first_time=bars[0].end_time if bars else None,
        last_time=bars[-1].end_time if bars else None,
    )
    seen: set[datetime] = set()
    prev: MarketBar | None = None
    for bar in bars:
        if bar.end_time in seen:
            report.issues.append(
                ValidationIssue(bar.end_time, QualityFlag.DUPLICATE_TIMESTAMP, "repeated end_time")
            )
        seen.add(bar.end_time)

        if prev is not None and bar.end_time <= prev.end_time:
            report.issues.append(
                ValidationIssue(bar.end_time, QualityFlag.OUT_OF_ORDER, "end_time not increasing")
            )

        hi = max(bar.open, bar.close)
        lo = min(bar.open, bar.close)
        if bar.high < hi or bar.low > lo or bar.high < bar.low:
            report.issues.append(
                ValidationIssue(
                    bar.end_time,
                    QualityFlag.INCONSISTENT_OHLC,
                    f"O={bar.open} H={bar.high} L={bar.low} C={bar.close}",
                )
            )

        if bar.spread is not None and bar.spread < 0:
            report.issues.append(
                ValidationIssue(bar.end_time, QualityFlag.NEGATIVE_SPREAD, f"spread={bar.spread}")
            )

        if bar.available_time < bar.end_time:
            report.issues.append(
                ValidationIssue(
                    bar.end_time,
                    QualityFlag.OUT_OF_ORDER,
                    "available_time earlier than end_time",
                )
            )
        prev = bar
    return report


def staleness_bars(as_of: datetime, last_available: datetime, bar_seconds: int) -> float:
    """How many bar-lengths old the freshest observation is at decision time."""
    if bar_seconds <= 0:
        return 0.0
    return (as_of - last_available).total_seconds() / bar_seconds
