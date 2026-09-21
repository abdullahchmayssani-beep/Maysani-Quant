"""Dukascopy historical tick provider (ADR 0003).

Only this module is allowed to know Dukascopy's URL scheme and byte layout.
Nothing outside `data/providers/dukascopy.py` may import it directly except
through `MarketDataProvider`.

## [UNVERIFIED] format notes

Dukascopy's historical tick feed is not covered by any official machine-
readable spec this session could reach (outbound network access to
`datafeed.dukascopy.com` is denied by this sandbox's egress policy - see
`docs/STATUS.md`). The layout below matches the format used by widely known
open-source Dukascopy downloaders (e.g. duka, dukascopy-node,
dukascopy-tools), reproduced here as engineering common knowledge about a
public URL scheme, not as licensed data. It is marked [UNVERIFIED] and must
be confirmed against a real downloaded sample (or Dukascopy's own docs)
before any output of this adapter is described as measuring real EUR/USD -
see "Real-data baseline" in the completion report for the current status of
that confirmation.

- URL: `https://datafeed.dukascopy.com/datafeed/{SYMBOL}/{YYYY}/{MM}/{DD}/{HH}h_ticks.bi5`
  where `MM` is **zero-indexed** (January = "00").
- Body: raw LZMA stream (no `.xz`/`.7z` container). An hour with no ticks
  (e.g. a weekend hour) is served as an empty (zero-byte) body.
- Each decompressed record is 20 bytes, big-endian:
  `uint32 time_offset_ms, int32 ask_raw, int32 bid_raw, float32 ask_volume,
  float32 bid_volume`. `time_offset_ms` is milliseconds since the top of the
  requested hour. `ask_raw`/`bid_raw` are the price multiplied by the
  instrument's point value (decimal precision); this adapter takes that
  point value from the run's already-configured `InstrumentSpec.price_precision`
  (`10 ** price_precision`) rather than hard-coding a Dukascopy-specific
  constant, since V0.1 already declares EUR/USD's precision as 5 (Section 21).
  Volume units are [UNVERIFIED] - not independently confirmed in this session.
"""
from __future__ import annotations

import lzma
import struct
import urllib.request
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime, timedelta

from maysani_quant.data.providers.base import (
    ArtifactParseError,
    ArtifactRetrievalError,
    ProviderTick,
    RawArtifact,
)

PROVIDER_NAME = "dukascopy"
PROVIDER_VERSION = "1.0.0-unverified"

_RECORD_STRUCT = struct.Struct(">Iiiff")  # ms, ask_raw, bid_raw, ask_volume, bid_volume
_RECORD_SIZE = _RECORD_STRUCT.size  # 20 bytes


def _hour_starts(start: datetime, end: datetime) -> Iterator[datetime]:
    if start.tzinfo is None or end.tzinfo is None:
        raise ValueError("start/end must be timezone-aware (UTC) - no timezone is ever guessed")
    cursor = start.astimezone(UTC).replace(minute=0, second=0, microsecond=0)
    end_utc = end.astimezone(UTC)
    while cursor < end_utc:
        yield cursor
        cursor += timedelta(hours=1)


def _url_for(instrument: str, hour_start: datetime) -> str:
    return (
        "https://datafeed.dukascopy.com/datafeed/"
        f"{instrument}/{hour_start.year:04d}/{hour_start.month - 1:02d}/"
        f"{hour_start.day:02d}/{hour_start.hour:02d}h_ticks.bi5"
    )


class DukascopyProvider:
    """FETCH via plain HTTP GET, PARSE via LZMA + struct.

    `price_precision` must come from the run's `InstrumentSpec` - it is a
    constructor argument, never a Dukascopy-specific literal, so a change to
    instrument precision in config cannot silently desync from this adapter.
    """

    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self, price_precision: int, timeout_seconds: float = 30.0) -> None:
        self.point_value = 10**price_precision
        self.timeout_seconds = timeout_seconds

    def fetch_artifacts(
        self, instrument: str, start: datetime, end: datetime
    ) -> Iterator[RawArtifact]:
        for hour_start in _hour_starts(start, end):
            hour_end = hour_start + timedelta(hours=1)
            url = _url_for(instrument, hour_start)
            retrieved_at = datetime.now(UTC)
            try:
                with urllib.request.urlopen(url, timeout=self.timeout_seconds) as response:  # noqa: S310
                    content = response.read()
            except Exception as exc:  # noqa: BLE001 - re-raised with context
                raise ArtifactRetrievalError(f"failed to fetch {url}: {exc}") from exc
            yield RawArtifact(
                provider=self.provider_name,
                provider_version=self.provider_version,
                instrument=instrument,
                requested_start=hour_start,
                requested_end=hour_end,
                retrieved_at=retrieved_at,
                source_uri=url,
                content=content,
            )

    def parse_artifacts(self, group: Sequence[RawArtifact]) -> Iterator[ProviderTick]:
        """A `.bi5` hour is self-contained - `group` is always a singleton in
        practice (ADR 0004) - but the loop costs nothing and keeps this
        adapter honest about the general contract."""
        for artifact in group:
            if not artifact.content:
                continue  # a genuinely empty hour (e.g. weekend close) has no ticks
            try:
                raw = lzma.decompress(artifact.content)
            except lzma.LZMAError as exc:
                raise ArtifactParseError(
                    f"artifact {artifact.source_uri} is not a valid LZMA stream: {exc}"
                ) from exc
            if len(raw) % _RECORD_SIZE != 0:
                raise ArtifactParseError(
                    f"artifact {artifact.source_uri} decompressed to {len(raw)} bytes, "
                    f"not a multiple of the {_RECORD_SIZE}-byte record size"
                )
            hour_start = artifact.requested_start
            for offset in range(0, len(raw), _RECORD_SIZE):
                ms, ask_raw, bid_raw, ask_volume, bid_volume = _RECORD_STRUCT.unpack_from(
                    raw, offset
                )
                yield ProviderTick(
                    instrument=artifact.instrument,
                    timestamp=hour_start + timedelta(milliseconds=ms),
                    bid=bid_raw / self.point_value,
                    ask=ask_raw / self.point_value,
                    bid_volume=bid_volume,
                    ask_volume=ask_volume,
                )
