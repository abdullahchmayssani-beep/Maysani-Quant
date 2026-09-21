"""CANONICAL VALIDATE tests: severity semantics and FX-aware gap detection.

Distinct from `tests/unit/test_point_in_time.py` (V0.1's `validate_bars` is
untested here on purpose - see `docs/adr/0003`).
"""
from __future__ import annotations

import math
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from maysani_quant.data.pipeline.canonical_validate import validate_canonical_bars
from maysani_quant.domain.enums import QualityFlag, QualitySeverity
from maysani_quant.domain.models import MarketBar

H = 3600


def _bar(start: datetime, *, close: float = 1.1, spread: float = 0.0001, **overrides) -> MarketBar:
    end = start + timedelta(seconds=H)
    fields = dict(
        instrument="EURUSD",
        start_time=start,
        end_time=end,
        available_time=end,
        open=close,
        high=close + 0.0002,
        low=close - 0.0002,
        close=close,
        bid_close=close - spread / 2,
        ask_close=close + spread / 2,
        spread=spread,
        source="test",
    )
    fields.update(overrides)
    return MarketBar(**fields)


def test_clean_series_is_valid_with_no_issues():
    start = datetime(2024, 1, 3, 8, tzinfo=UTC)  # a Wednesday
    bars = [_bar(start + timedelta(hours=i)) for i in range(5)]
    report = validate_canonical_bars(bars, expected_bar_seconds=H)
    assert report.severity is QualitySeverity.VALID
    assert report.ok
    assert report.issues == []


def test_non_finite_value_is_invalid():
    start = datetime(2024, 1, 3, 8, tzinfo=UTC)
    bars = [_bar(start), _bar(start + timedelta(hours=1), close=math.nan)]
    report = validate_canonical_bars(bars, expected_bar_seconds=H)
    assert report.severity is QualitySeverity.INVALID
    assert not report.ok
    assert any(i.flag is QualityFlag.NON_FINITE for i in report.issues)


def test_bid_above_ask_is_invalid():
    start = datetime(2024, 1, 3, 8, tzinfo=UTC)
    bar = _bar(start)
    # force an impossible quote: ask below bid
    bad = replace(bar, bid_close=1.2000, ask_close=1.1000, spread=-0.1)
    report = validate_canonical_bars([bad], expected_bar_seconds=H)
    assert not report.ok
    assert any(i.flag is QualityFlag.NEGATIVE_SPREAD for i in report.issues)


def test_duplicate_timestamp_is_invalid():
    start = datetime(2024, 1, 3, 8, tzinfo=UTC)
    bars = [_bar(start), _bar(start)]
    report = validate_canonical_bars(bars, expected_bar_seconds=H)
    assert not report.ok
    assert any(i.flag is QualityFlag.DUPLICATE_TIMESTAMP for i in report.issues)


def test_naive_timestamp_is_invalid():
    naive_start = datetime(2024, 1, 3, 8)  # no tzinfo
    bar = _bar(datetime(2024, 1, 3, 8, tzinfo=UTC))
    bad = replace(bar, start_time=naive_start)
    report = validate_canonical_bars([bad], expected_bar_seconds=H)
    assert not report.ok
    assert any(i.flag is QualityFlag.TIMEZONE_NAIVE for i in report.issues)


def test_require_bid_ask_flags_missing_quotes():
    start = datetime(2024, 1, 3, 8, tzinfo=UTC)
    bar = _bar(start)
    midpoint_only = replace(bar, bid_close=None, ask_close=None, spread=None)
    report = validate_canonical_bars(
        [midpoint_only], expected_bar_seconds=H, require_bid_ask=True
    )
    assert not report.ok

    report_lenient = validate_canonical_bars(
        [midpoint_only], expected_bar_seconds=H, require_bid_ask=False
    )
    assert report_lenient.ok


def test_weekend_closure_gap_is_valid_not_suspicious():
    """Friday 20:00 UTC close -> Monday 00:00 UTC reopen is expected FX
    market structure, not missing data (ADR 0003 s.6)."""
    friday_bar_start = datetime(2024, 1, 5, 20, tzinfo=UTC)  # Friday
    monday_bar_start = datetime(2024, 1, 8, 0, tzinfo=UTC)  # Monday, > 2 days later
    bars = [_bar(friday_bar_start), _bar(monday_bar_start)]
    report = validate_canonical_bars(bars, expected_bar_seconds=H)
    flags = {i.flag for i in report.issues}
    assert QualityFlag.WEEKEND_GAP in flags
    assert QualityFlag.SUSPICIOUS_GAP not in flags
    assert report.ok  # weekend gaps are VALID severity


def test_midweek_gap_is_suspicious_not_weekend():
    tuesday_bar_start = datetime(2024, 1, 2, 8, tzinfo=UTC)  # Tuesday
    later_same_day = datetime(2024, 1, 2, 14, tzinfo=UTC)  # 5 missing hours, midweek
    bars = [_bar(tuesday_bar_start), _bar(later_same_day)]
    report = validate_canonical_bars(bars, expected_bar_seconds=H)
    flags = {i.flag for i in report.issues}
    assert QualityFlag.SUSPICIOUS_GAP in flags
    assert QualityFlag.WEEKEND_GAP not in flags
    assert report.ok  # WARNING severity, not INVALID - usable but surfaced
    assert report.severity is QualitySeverity.WARNING


def test_contiguous_bars_produce_no_gap_flag():
    start = datetime(2024, 1, 3, 8, tzinfo=UTC)
    bars = [_bar(start), _bar(start + timedelta(hours=1)), _bar(start + timedelta(hours=2))]
    report = validate_canonical_bars(bars, expected_bar_seconds=H)
    assert not any(
        i.flag in (QualityFlag.WEEKEND_GAP, QualityFlag.SUSPICIOUS_GAP) for i in report.issues
    )
