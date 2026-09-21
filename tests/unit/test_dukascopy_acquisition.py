"""Automatic acquisition tests (ADR 0005) - all offline, deterministic.

No test in this module opens a real socket: `DukascopyProvider`'s `opener`
and `sleep_fn` constructor seams are always replaced with in-memory fakes.
This proves the retry/backoff/cache-hit/outcome behaviour without touching
the network, per the V0.2.1 requirement that CI stay fully offline.
"""
from __future__ import annotations

import lzma
import struct
import urllib.error
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from maysani_quant.data.pipeline.raw_store import RawArtifactStore
from maysani_quant.data.providers.base import ArtifactParseError
from maysani_quant.data.providers.dukascopy import DukascopyProvider
from maysani_quant.data.service import MarketDataService

START = datetime(2024, 1, 3, 10, tzinfo=UTC)
ONE_HOUR = timedelta(hours=1)


def _bi5(records: list[tuple[int, int, int, float, float]]) -> bytes:
    raw = b"".join(struct.pack(">Iiiff", *r) for r in records)
    return lzma.compress(raw)


GOOD_BYTES = _bi5([(0, 108234, 108220, 1.0, 1.0)])


def _service(provider: DukascopyProvider, tmp_path: Path, *, end: datetime = START + ONE_HOUR):
    return MarketDataService(
        provider,
        instrument="EURUSD",
        start=START,
        end=end,
        bar_seconds=3600,
        timeframe="H1",
        raw_root=tmp_path / "raw",
        canonical_root=tmp_path / "canonical",
        require_bid_ask=False,
    )


def test_successful_acquisition_all_downloaded(tmp_path: Path):
    calls = []

    def opener(url, timeout):
        calls.append(url)
        return GOOD_BYTES

    provider = DukascopyProvider(price_precision=5, opener=opener, sleep_fn=lambda s: None)
    svc = _service(provider, tmp_path)
    assert len(calls) == 1
    assert [o.status for o in provider.outcomes] == ["downloaded"]
    assert provider.outcomes[0].attempts == 1
    assert len(svc.all_bars()) == 1
    assert svc.validation.ok


def test_repeat_acquisition_is_a_cache_hit_with_no_network_calls(tmp_path: Path):
    calls = []

    def opener(url, timeout):
        calls.append(url)
        return GOOD_BYTES

    provider_a = DukascopyProvider(price_precision=5, opener=opener, sleep_fn=lambda s: None)
    svc_a = _service(provider_a, tmp_path)
    assert len(calls) == 1

    provider_b = DukascopyProvider(price_precision=5, opener=opener, sleep_fn=lambda s: None)
    svc_b = _service(provider_b, tmp_path)
    assert len(calls) == 1, "second run must not hit the network again"
    assert [o.status for o in provider_b.outcomes] == ["cache_hit"]
    assert svc_a.data_hash == svc_b.data_hash
    assert [b.close for b in svc_a.all_bars()] == [b.close for b in svc_b.all_bars()]


def test_transient_failure_then_success_is_retried_with_backoff(tmp_path: Path):
    calls = []
    sleeps = []

    def flaky(url, timeout):
        calls.append(url)
        if len(calls) <= 2:
            raise TimeoutError("simulated transient failure")
        return GOOD_BYTES

    provider = DukascopyProvider(
        price_precision=5, opener=flaky, sleep_fn=sleeps.append, max_attempts=4
    )
    svc = _service(provider, tmp_path)
    assert len(calls) == 3
    assert provider.outcomes[0].status == "downloaded"
    assert provider.outcomes[0].attempts == 3
    assert sleeps == [1.0, 2.0]  # exponential backoff, base=1.0
    assert len(svc.all_bars()) == 1


def test_persistent_timeout_exhausts_bounded_retries_and_is_reported_failed(tmp_path: Path):
    sleeps = []

    def always_times_out(url, timeout):
        raise TimeoutError("always times out")

    provider = DukascopyProvider(
        price_precision=5, opener=always_times_out, sleep_fn=sleeps.append, max_attempts=3
    )
    svc = _service(provider, tmp_path)
    assert provider.outcomes[0].status == "failed"
    assert provider.outcomes[0].attempts == 3
    assert len(sleeps) == 2, "exactly max_attempts - 1 backoffs - never an unbounded retry loop"
    assert len(svc.all_bars()) == 0
    assert svc.manifest.bar_count == 0


def test_http_4xx_is_reported_missing_without_retry(tmp_path: Path):
    sleeps = []

    def not_found(url, timeout):
        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

    provider = DukascopyProvider(
        price_precision=5, opener=not_found, sleep_fn=sleeps.append, max_attempts=4
    )
    svc = _service(provider, tmp_path)
    assert provider.outcomes[0].status == "missing"
    assert provider.outcomes[0].attempts == 1, "a 4xx must never be retried"
    assert sleeps == []
    assert len(svc.all_bars()) == 0


def test_http_5xx_is_treated_as_transient_and_retried(tmp_path: Path):
    calls = []

    def server_error_then_ok(url, timeout):
        calls.append(url)
        if len(calls) == 1:
            raise urllib.error.HTTPError(url, 503, "Service Unavailable", {}, None)
        return GOOD_BYTES

    provider = DukascopyProvider(
        price_precision=5, opener=server_error_then_ok, sleep_fn=lambda s: None, max_attempts=3
    )
    svc = _service(provider, tmp_path)
    assert provider.outcomes[0].status == "downloaded"
    assert provider.outcomes[0].attempts == 2
    assert len(svc.all_bars()) == 1


def test_missing_hour_gap_does_not_abort_the_rest_of_the_window(tmp_path: Path):
    """One 404'd hour must not prevent the other hours in the window from
    being acquired - the gap surfaces later in canonical validation."""
    hour0_url_seen = []

    def opener(url, timeout):
        if "10h_ticks" in url:
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)
        hour0_url_seen.append(url)
        return GOOD_BYTES

    provider = DukascopyProvider(price_precision=5, opener=opener, sleep_fn=lambda s: None)
    svc = _service(provider, tmp_path, end=START + timedelta(hours=2))
    statuses = {o.hour_start.hour: o.status for o in provider.outcomes}
    assert statuses == {10: "missing", 11: "downloaded"}
    assert len(svc.all_bars()) == 1  # the 11:00 hour still made it through


def test_corrupt_bytes_are_downloaded_successfully_but_parse_raises(tmp_path: Path):
    """FETCH-level success does not mean the content is trustworthy - a
    corrupt-but-200 response must surface as a hard PARSE failure, never a
    silently accepted or silently dropped hour."""

    def corrupt(url, timeout):
        return b"not a valid lzma stream at all"

    provider = DukascopyProvider(price_precision=5, opener=corrupt, sleep_fn=lambda s: None)
    with pytest.raises(ArtifactParseError):
        _service(provider, tmp_path)
    assert provider.outcomes[0].status == "downloaded"


def test_empty_hour_is_downloaded_with_zero_ticks_not_reported_missing(tmp_path: Path):
    """A confirmed-empty 200 (e.g. a weekend hour, per the documented
    [UNVERIFIED] assumption) is distinct from a 4xx 'missing' hour."""

    def empty_200(url, timeout):
        return b""

    provider = DukascopyProvider(price_precision=5, opener=empty_200, sleep_fn=lambda s: None)
    svc = _service(provider, tmp_path)
    assert provider.outcomes[0].status == "downloaded"
    assert len(svc.all_bars()) == 0


def test_find_by_request_self_heals_on_deleted_blob(tmp_path: Path):
    """If the raw cache directory is partially wiped, a stale index entry
    must be treated as a cache miss, never as a crash or fabricated hit."""
    store = RawArtifactStore(tmp_path / "raw")
    calls = []

    def opener(url, timeout):
        calls.append(url)
        return GOOD_BYTES

    provider = DukascopyProvider(
        price_precision=5, opener=opener, sleep_fn=lambda s: None, raw_store=store
    )
    list(provider.fetch_artifacts("EURUSD", START, START + ONE_HOUR))
    assert len(calls) == 1

    # Simulate partial corruption: delete the blob but leave the index.
    for blob in (tmp_path / "raw").rglob("*.bin"):
        blob.unlink()

    list(provider.fetch_artifacts("EURUSD", START, START + ONE_HOUR))
    assert len(calls) == 2, "a missing blob must fall back to a real fetch, not crash or fabricate"
