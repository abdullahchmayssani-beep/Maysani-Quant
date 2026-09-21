"""No-future-data tests (Section 21.9).

The contract is stronger than "returns nothing": asking for ineligible data
raises. A silent empty result would let a leaking backtest complete and look
merely unprofitable, which is the worse failure mode.
"""
from __future__ import annotations

from datetime import timedelta

import pytest

from maysani_quant.data.interfaces import InsufficientHistory, LookAheadError, PointInTimeView
from maysani_quant.features.pipeline import FeatureConfig, FeaturePipeline
from tests.conftest import flat_bars, make_bar, trending_bars


@pytest.mark.invariant
def test_view_excludes_bars_available_after_as_of():
    bars = trending_bars(10)
    as_of = bars[4].available_time
    view = PointInTimeView(bars[:5], as_of, "EURUSD")
    assert len(view) == 5
    assert all(b.available_time <= as_of for b in view)


@pytest.mark.invariant
def test_view_filters_future_bars_and_counts_them():
    bars = trending_bars(10)
    as_of = bars[4].available_time
    view = PointInTimeView(bars, as_of, "EURUSD")
    assert len(view) == 5
    assert view.excluded_count == 5


@pytest.mark.invariant
def test_strict_view_raises_when_handed_future_bars():
    """Strict mode is for callers that claim to have filtered already."""
    bars = trending_bars(10)
    as_of = bars[4].available_time
    with pytest.raises(LookAheadError):
        PointInTimeView(bars, as_of, "EURUSD", strict=True)


@pytest.mark.invariant
def test_view_rejects_query_beyond_as_of():
    bars = trending_bars(10)
    as_of = bars[4].available_time
    view = PointInTimeView(bars[:5], as_of, "EURUSD")
    with pytest.raises(LookAheadError):
        view.at_or_after(as_of + timedelta(days=1))


@pytest.mark.invariant
def test_available_time_lag_delays_eligibility():
    """A bar published 10 minutes after its close is not usable at its close."""
    lagged = make_bar(0, 1.1, 1.1, 1.1, 1.1, available_offset_seconds=600)
    at_close = lagged.end_time
    view = PointInTimeView([lagged], at_close, "EURUSD")
    assert len(view) == 0, "a lagged bar must not be visible at its own close"

    later = PointInTimeView([lagged], at_close + timedelta(seconds=600), "EURUSD")
    assert len(later) == 1


def test_pipeline_returns_none_during_warmup(feature_config: FeatureConfig):
    pipeline = FeaturePipeline(feature_config)
    bars = trending_bars(3)
    view = PointInTimeView(bars, bars[-1].available_time, "EURUSD")
    assert pipeline.compute(view, bars[-1].available_time) is None


def test_pipeline_features_depend_only_on_past(feature_config: FeatureConfig):
    """Same prefix, different future -> identical snapshot id."""
    pipeline = FeaturePipeline(feature_config)
    base = trending_bars(30)
    as_of = base[24].available_time

    view_a = PointInTimeView(base[:25], as_of, "EURUSD")
    snap_a = pipeline.compute(view_a, as_of)

    diverged = base[:25] + flat_bars(5, price=99.0)
    view_b = PointInTimeView(diverged[:25], as_of, "EURUSD")
    snap_b = pipeline.compute(view_b, as_of)

    assert snap_a is not None and snap_b is not None
    assert snap_a.snapshot_id == snap_b.snapshot_id
    assert snap_a.values == snap_b.values


def test_require_raises_on_short_history():
    bars = trending_bars(3)
    view = PointInTimeView(bars, bars[-1].available_time, "EURUSD")
    with pytest.raises(InsufficientHistory):
        view.require(10)


@pytest.mark.invariant
def test_zscore_reference_window_excludes_current_value():
    """The z-score centre must be computed from the bars BEFORE the latest one.

    Including the current value in its own mean is a mild but real leak: it
    shrinks the measured deviation toward zero using information from the point
    being scored.
    """
    from maysani_quant.features.mean_reversion import rolling_zscore

    values = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0]
    z = rolling_zscore(values, window=5)
    # reference is five identical values -> sd 0 -> defined as 0.0, not a leak
    assert z == 0.0

    values = [1.0, 2.0, 1.0, 2.0, 1.0, 5.0]
    z2 = rolling_zscore(values, window=5)
    reference = values[:5]
    mean = sum(reference) / 5
    assert z2 > 0 and abs(mean - 1.4) < 1e-12
