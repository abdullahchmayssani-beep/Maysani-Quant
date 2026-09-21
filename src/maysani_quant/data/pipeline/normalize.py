"""NORMALIZE: provider-agnostic tick -> canonical `MarketBar` aggregation.

Takes the provider-agnostic `ProviderTick` stream produced by any adapter's
PARSE step and aggregates it into `MarketBar`s on a configured timeframe.
Nothing here is Dukascopy-specific; a second tick-shaped provider needs no
changes to this module. Bar-shaped providers (should one ever exist) would
skip this stage entirely and hand `MarketBar`s straight to CANONICAL
VALIDATE.

Aggregation policy (ADR 0003 s.4), fixed and documented rather than
guessed at call sites:

- OHLC is computed from mid price `(bid+ask)/2` per tick, consistent with
  V0.1's existing `price_kind: midpoint` convention.
- `bid_close`/`ask_close` are the last tick's bid/ask in the bar window;
  `spread = ask_close - bid_close`.
- `volume` is summed bid+ask tick volume in the window.
- No value is repaired here. A non-finite tick produces a non-finite bar,
  which CANONICAL VALIDATE (not this module) is responsible for flagging.
"""
from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

from maysani_quant.data.providers.base import ProviderTick
from maysani_quant.domain.enums import QualityFlag
from maysani_quant.domain.models import MarketBar

OHLC_PRICE_KIND = "midpoint"


def _resolve_available_time(
    end_time: datetime, policy: str, lag_seconds: int
) -> datetime:
    if policy == "bar_close":
        return end_time
    if policy == "bar_close_plus_lag":
        return end_time + timedelta(seconds=lag_seconds)
    raise ValueError(f"unknown available_time_policy: {policy}")


def normalize_ticks_to_bars(
    ticks: Iterable[ProviderTick],
    *,
    instrument: str,
    bar_seconds: int,
    available_time_policy: str,
    available_time_lag_seconds: int,
    source_tag: str,
) -> list[MarketBar]:
    if bar_seconds <= 0:
        raise ValueError("bar_seconds must be positive")

    buckets: dict[int, list[ProviderTick]] = {}
    for tick in ticks:
        bucket_index = int(tick.timestamp.timestamp() // bar_seconds)
        buckets.setdefault(bucket_index, []).append(tick)

    bars: list[MarketBar] = []
    for bucket_index in sorted(buckets):
        group = sorted(buckets[bucket_index], key=lambda t: t.timestamp)
        start = datetime.fromtimestamp(bucket_index * bar_seconds, tz=UTC)
        end = start + timedelta(seconds=bar_seconds)
        mids = [(t.bid + t.ask) / 2.0 for t in group]
        last = group[-1]
        bars.append(
            MarketBar(
                instrument=instrument,
                start_time=start,
                end_time=end,
                available_time=_resolve_available_time(
                    end, available_time_policy, available_time_lag_seconds
                ),
                open=mids[0],
                high=max(mids),
                low=min(mids),
                close=mids[-1],
                volume=sum(t.bid_volume + t.ask_volume for t in group),
                bid_close=last.bid,
                ask_close=last.ask,
                spread=last.ask - last.bid,
                source=source_tag,
                quality_flags=(QualityFlag.OK,),
            )
        )
    return bars
