"""Regression tests for the V0.2 pre-freeze audit findings.

Each test here pins a defect the audit found in code whose existing tests
were all passing. They are grouped in one module so the freeze review can
see, in one place, exactly what was wrong and what now prevents it.
"""
from __future__ import annotations

import json
import lzma
import struct
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from maysani_quant.config import BAR_SECONDS, load_config
from maysani_quant.data.pipeline.canonical_store import CanonicalIntegrityError, CanonicalStore
from maysani_quant.data.pipeline.canonical_validate import validate_canonical_bars
from maysani_quant.data.pipeline.raw_store import RawArtifactStore
from maysani_quant.data.provenance import (
    SCHEMA_VERSION,
    CanonicalManifest,
    NormalizationPolicy,
)
from maysani_quant.data.providers.base import ArtifactParseError, RawArtifact
from maysani_quant.data.providers.dukascopy import DukascopyProvider
from maysani_quant.domain.enums import QualityFlag, QualitySeverity
from maysani_quant.domain.models import MarketBar

HOUR = datetime(2024, 1, 3, 10, tzinfo=UTC)


def _bar(start: datetime, *, hours: int = 1, close: float = 1.1, **overrides) -> MarketBar:
    end = start + timedelta(hours=hours)
    fields = dict(
        instrument="EURUSD",
        start_time=start,
        end_time=end,
        available_time=end,
        open=close,
        high=close,
        low=close,
        close=close,
        bid_close=close - 0.00005,
        ask_close=close + 0.00005,
        spread=0.0001,
        source="test",
    )
    fields.update(overrides)
    return MarketBar(**fields)


# --------------------------------------------------------------- validation
def test_non_positive_prices_are_invalid():
    """A uniformly negative bar is finite, OHLC-consistent and has a positive
    ask-bid spread, so every other check passed it as VALID."""
    bad = _bar(HOUR, close=-1.1, bid_close=-1.11, ask_close=-1.09, spread=0.02)
    report = validate_canonical_bars([bad], expected_bar_seconds=3600)
    assert not report.ok
    assert any(i.flag is QualityFlag.NON_POSITIVE_PRICE for i in report.issues)

    zero = _bar(HOUR, close=0.0, bid_close=0.0, ask_close=0.0, spread=0.0)
    assert not validate_canonical_bars([zero], expected_bar_seconds=3600).ok


def test_mid_week_hole_starting_in_the_weekend_window_is_not_a_weekend_gap():
    """The classifier only looked at where a gap STARTED, so a ~3-day hole
    that began on a Sunday evening was reported VALID and vanished from the
    quality summary."""
    sunday_evening = datetime(2024, 1, 7, 19, tzinfo=UTC)  # inside the closure window
    wednesday = datetime(2024, 1, 10, 17, tzinfo=UTC)  # ~2.9 days later, mid-week
    report = validate_canonical_bars(
        [_bar(sunday_evening), _bar(wednesday)], expected_bar_seconds=3600
    )
    flags = {i.flag for i in report.issues}
    assert QualityFlag.SUSPICIOUS_GAP in flags
    assert QualityFlag.WEEKEND_GAP not in flags
    assert report.severity is QualitySeverity.WARNING


def test_a_genuine_weekend_closure_is_still_valid():
    """The fix must not turn ordinary Friday-close -> Monday-open gaps into
    warnings."""
    friday_close = datetime(2024, 1, 5, 20, tzinfo=UTC)  # bar ends Fri 21:00
    monday_open = datetime(2024, 1, 8, 0, tzinfo=UTC)
    report = validate_canonical_bars(
        [_bar(friday_close), _bar(monday_open)], expected_bar_seconds=3600
    )
    flags = {i.flag for i in report.issues}
    assert QualityFlag.WEEKEND_GAP in flags
    assert QualityFlag.SUSPICIOUS_GAP not in flags
    assert report.ok


# ------------------------------------------------------------- bi5 PARSE
def _artifact(content: bytes, *, hours: int = 1) -> RawArtifact:
    return RawArtifact(
        provider="dukascopy",
        provider_version="test",
        instrument="EURUSD",
        requested_start=HOUR,
        requested_end=HOUR + timedelta(hours=hours),
        retrieved_at=HOUR,
        source_uri="test://fixture",
        content=content,
    )


def test_tick_offset_outside_the_declared_hour_is_rejected():
    """A record whose millisecond offset lands outside the hour the artifact
    declares means the bytes are not this adapter's [UNVERIFIED] layout.
    Emitting the tick anyway placed a bar at a fabricated time, where it
    produced at most a WARNING-level gap."""
    provider = DukascopyProvider(price_precision=5)
    out_of_hour = 4_000_000_000  # ~46 days past the hour start
    raw = struct.pack(">Iiiff", out_of_hour, 108234, 108220, 1.0, 1.0)
    with pytest.raises(ArtifactParseError, match="outside its declared"):
        list(provider.parse_artifacts([_artifact(lzma.compress(raw))]))


def test_tick_at_the_last_millisecond_of_the_hour_is_accepted():
    """The bound is exclusive at the hour end, not over-tight."""
    provider = DukascopyProvider(price_precision=5)
    raw = struct.pack(">Iiiff", 3_599_999, 108234, 108220, 1.0, 1.0)
    ticks = list(provider.parse_artifacts([_artifact(lzma.compress(raw))]))
    assert len(ticks) == 1
    assert ticks[0].timestamp == HOUR + timedelta(milliseconds=3_599_999)


# --------------------------------------------------------------- raw store
def test_request_index_keeps_bid_and_ask_of_one_window_apart():
    """Both artifacts of an ADR 0004 CSV-export window share a requested
    window; a label-less index key made the second overwrite the first."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        store = RawArtifactStore(tmp)
        bid = RawArtifact(
            provider="dukascopy_csv_export", provider_version="t", instrument="EURUSD",
            requested_start=HOUR, requested_end=HOUR + timedelta(hours=1),
            retrieved_at=HOUR, source_uri="file://bid", content=b"bid-bytes", label="bid",
        )
        ask = RawArtifact(**{**bid.__dict__, "content": b"ask-bytes", "label": "ask",
                             "source_uri": "file://ask"})
        bid_manifest = store.put(bid)
        ask_manifest = store.put(ask)
        assert bid_manifest.sha256 != ask_manifest.sha256

        found_bid = store.find_by_request(
            "dukascopy_csv_export", "EURUSD", HOUR, HOUR + timedelta(hours=1), "bid"
        )
        found_ask = store.find_by_request(
            "dukascopy_csv_export", "EURUSD", HOUR, HOUR + timedelta(hours=1), "ask"
        )
        assert found_bid is not None and found_ask is not None
        assert found_bid.sha256 == bid_manifest.sha256
        assert found_ask.sha256 == ask_manifest.sha256


def test_manifest_is_restored_when_only_the_sidecar_is_missing(tmp_path: Path):
    """A blob whose manifest went missing stayed un-provenanced forever and
    could never become a cache hit again, because put() only wrote the
    sidecar on the branch that wrote the blob."""
    store = RawArtifactStore(tmp_path)
    artifact = _artifact(b"some bytes")
    manifest = store.put(artifact)

    _, manifest_path = store._paths("dukascopy", "EURUSD", manifest.sha256)
    manifest_path.unlink()
    assert store.find_by_request("dukascopy", "EURUSD", HOUR, HOUR + timedelta(hours=1)) is None

    store.put(artifact)  # same bytes, blob already present
    assert manifest_path.exists()
    assert store.find_by_request("dukascopy", "EURUSD", HOUR, HOUR + timedelta(hours=1)) is not None


# ---------------------------------------------------------- canonical store
def _manifest(identity: str = "deadbeef") -> CanonicalManifest:
    return CanonicalManifest(
        canonical_identity_hash=identity,
        raw_artifact_hashes=("aaaa",),
        provider="dukascopy",
        provider_version="test",
        instrument="EURUSD",
        requested_start=HOUR,
        requested_end=HOUR + timedelta(hours=1),
        schema_version=SCHEMA_VERSION,
        normalization_policy=NormalizationPolicy("H1", "bar_close", 0, "midpoint"),
        pipeline_version="pipeline-v1",
        retrieved_at=HOUR,
        bar_count=1,
    )


def test_edited_canonical_cache_cannot_be_served_under_its_identity(tmp_path: Path):
    """The identity hash covers the pipeline's inputs. Without a checksum on
    the output, an edited or truncated cache file was still served - and the
    experiment registry would cite an identity that no longer described the
    bars actually backtested."""
    store = CanonicalStore(tmp_path)
    stamped = store.write(_manifest(), [_bar(HOUR)])
    assert stamped.bars_sha256, "write() must record the bars checksum"
    assert store.read_bars("dukascopy", "EURUSD", "deadbeef")[0].close == pytest.approx(1.1)

    bars_path, _ = store.paths_for("dukascopy", "EURUSD", "deadbeef")
    bars_path.write_text(bars_path.read_text().replace("1.1", "9.9"), encoding="utf-8")
    with pytest.raises(CanonicalIntegrityError):
        store.read_bars("dukascopy", "EURUSD", "deadbeef")


def test_truncated_canonical_cache_is_rejected(tmp_path: Path):
    store = CanonicalStore(tmp_path)
    store.write(_manifest(), [_bar(HOUR), _bar(HOUR + timedelta(hours=1))])
    bars_path, _ = store.paths_for("dukascopy", "EURUSD", "deadbeef")
    lines = bars_path.read_text().splitlines(keepends=True)
    bars_path.write_text("".join(lines[:-1]), encoding="utf-8")
    with pytest.raises(CanonicalIntegrityError):
        store.read_bars("dukascopy", "EURUSD", "deadbeef")


def test_manifest_without_a_checksum_still_loads(tmp_path: Path):
    """Entries written before the checksum existed must not hard-fail; they
    are simply unverifiable."""
    store = CanonicalStore(tmp_path)
    store.write(_manifest(), [_bar(HOUR)])
    _, manifest_path = store.paths_for("dukascopy", "EURUSD", "deadbeef")
    data = json.loads(manifest_path.read_text())
    del data["bars_sha256"]
    manifest_path.write_text(json.dumps(data), encoding="utf-8")
    assert len(store.read_bars("dukascopy", "EURUSD", "deadbeef")) == 1


# ---------------------------------------------------------------- config
def test_unknown_timeframe_raises_instead_of_silently_meaning_daily(tmp_path: Path):
    """`bar_seconds` fell back to 86400 for any unrecognised timeframe, so a
    typo silently reinterpreted an entire run as daily bars."""
    text = Path("configs/v0_1.yaml").read_text(encoding="utf-8")
    typo = tmp_path / "typo.yaml"
    typo.write_text(text.replace("timeframe: D1", "timeframe: D11"), encoding="utf-8")
    config = load_config(typo)
    with pytest.raises(ValueError, match="unknown data.timeframe"):
        _ = config.bar_seconds


def test_every_known_timeframe_still_resolves(tmp_path: Path):
    """The guard must reject only unknown names - every supported timeframe
    still loads and yields its documented bar length."""
    text = Path("configs/v0_1.yaml").read_text(encoding="utf-8")
    for name, seconds in BAR_SECONDS.items():
        path = tmp_path / f"{name}.yaml"
        path.write_text(text.replace("timeframe: D1", f"timeframe: {name}"), encoding="utf-8")
        assert load_config(path).bar_seconds == seconds
