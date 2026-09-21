"""Dukascopy historical tick provider (ADR 0003 / ADR 0005).

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
before any output of this adapter is described as measuring real EUR/USD.
Whether Dukascopy serves a missing/unpublished hour as HTTP 404, some other
4xx, or an empty 200 body is likewise [UNVERIFIED] from this sandbox; this
adapter handles all of those distinctly (see `AcquisitionOutcome`) rather
than assuming one.

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

## Acquisition model (ADR 0005)

FETCH is per-hour and never blocks the whole request on one bad hour: each
hour's outcome is one of `downloaded`, `cache_hit`, `missing` (a non-retryable
4xx - retrying a "this doesn't exist" response cannot help) or `failed` (a
transient/network-level failure that exhausted `max_attempts` bounded
retries with exponential backoff). `missing`/`failed` hours are skipped, not
fabricated - any resulting hole in the data surfaces downstream as a
`SUSPICIOUS_GAP`/`WEEKEND_GAP` in canonical validation, exactly like any
other gap. `self.outcomes` (populated fresh on every `fetch_artifacts` call)
is this adapter's own reporting surface, read by the `acquire-dukascopy` CLI
command - it is not part of the `MarketDataProvider` protocol, so other
providers are unaffected.

Retries never loop unboundedly: `max_attempts` bounds the total attempts per
hour, and only network-level failures and 5xx responses are retried at all -
a 4xx is recorded as `missing` on the first attempt.
"""
from __future__ import annotations

import lzma
import struct
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from maysani_quant.data.providers.base import (
    ArtifactParseError,
    ProviderTick,
    RawArtifact,
)

PROVIDER_NAME = "dukascopy"
PROVIDER_VERSION = "1.1.0-unverified"

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


def _default_opener(url: str, timeout_seconds: float) -> bytes:
    """The only place a real socket is opened. Tests inject a fake in place
    of this function - never monkeypatch urllib internals."""
    with urllib.request.urlopen(url, timeout=timeout_seconds) as response:  # noqa: S310
        return response.read()


@dataclass(frozen=True)
class AcquisitionOutcome:
    """One hour's FETCH result - this adapter's own reporting surface
    (ADR 0005), read by the `acquire-dukascopy` CLI. Not part of the
    `MarketDataProvider` protocol."""

    hour_start: datetime
    status: str  # "downloaded" | "cache_hit" | "missing" | "failed"
    attempts: int = 0
    detail: str = ""
    sha256: str | None = None


class DukascopyProvider:
    """FETCH via bounded-retry HTTP GET (optionally cache-aware), PARSE via
    LZMA + struct.

    `price_precision` must come from the run's `InstrumentSpec` - it is a
    constructor argument, never a Dukascopy-specific literal, so a change to
    instrument precision in config cannot silently desync from this adapter.

    `raw_store`, if set (typically auto-wired by `MarketDataService`, see
    ADR 0005), is consulted before every network attempt via
    `find_by_request` - an exact-window cache hit skips the network
    entirely. `opener` and `sleep_fn` are injectable seams for fully offline,
    deterministic testing (no real sockets, no real waiting).
    """

    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(
        self,
        price_precision: int,
        timeout_seconds: float = 30.0,
        max_attempts: int = 4,
        backoff_base_seconds: float = 1.0,
        backoff_cap_seconds: float = 30.0,
        raw_store: object | None = None,
        opener: Callable[[str, float], bytes] = _default_opener,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.point_value = 10**price_precision
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.backoff_base_seconds = backoff_base_seconds
        self.backoff_cap_seconds = backoff_cap_seconds
        self.raw_store = raw_store
        self._opener = opener
        self._sleep = sleep_fn
        self.outcomes: list[AcquisitionOutcome] = []

    def _fetch_one(self, url: str, hour_start: datetime) -> tuple[bytes | None, AcquisitionOutcome]:
        last_error = ""
        for attempt in range(1, self.max_attempts + 1):
            try:
                content = self._opener(url, self.timeout_seconds)
                return content, AcquisitionOutcome(hour_start, "downloaded", attempts=attempt)
            except urllib.error.HTTPError as exc:
                if 400 <= exc.code < 500:
                    return None, AcquisitionOutcome(
                        hour_start, "missing", attempts=attempt,
                        detail=f"HTTP {exc.code}: {exc.reason}",
                    )
                last_error = f"HTTP {exc.code}: {exc.reason}"
            except Exception as exc:  # noqa: BLE001 - transient failure, bounded retry below
                last_error = f"{type(exc).__name__}: {exc}"
            if attempt < self.max_attempts:
                backoff = min(self.backoff_base_seconds * (2 ** (attempt - 1)), self.backoff_cap_seconds)
                self._sleep(backoff)
        return None, AcquisitionOutcome(
            hour_start, "failed", attempts=self.max_attempts, detail=last_error
        )

    def fetch_artifacts(
        self, instrument: str, start: datetime, end: datetime
    ) -> Iterator[RawArtifact]:
        self.outcomes = []
        for hour_start in _hour_starts(start, end):
            hour_end = hour_start + timedelta(hours=1)

            if self.raw_store is not None:
                cached = self.raw_store.find_by_request(  # type: ignore[attr-defined]
                    self.provider_name, instrument, hour_start, hour_end
                )
                if cached is not None:
                    self.outcomes.append(
                        AcquisitionOutcome(hour_start, "cache_hit", sha256=cached.sha256)
                    )
                    content = self.raw_store.get_bytes(  # type: ignore[attr-defined]
                        self.provider_name, instrument, cached.sha256
                    )
                    yield RawArtifact(
                        provider=self.provider_name,
                        provider_version=self.provider_version,
                        instrument=instrument,
                        requested_start=hour_start,
                        requested_end=hour_end,
                        retrieved_at=cached.retrieved_at,
                        source_uri=cached.source_uri,
                        content=content,
                    )
                    continue

            url = _url_for(instrument, hour_start)
            content, outcome = self._fetch_one(url, hour_start)
            self.outcomes.append(outcome)
            if content is None:
                continue  # missing/failed - explicit in self.outcomes, never fabricated
            yield RawArtifact(
                provider=self.provider_name,
                provider_version=self.provider_version,
                instrument=instrument,
                requested_start=hour_start,
                requested_end=hour_end,
                retrieved_at=datetime.now(UTC),
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
