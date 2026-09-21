"""Dukascopy PARSE-stage tests (ADR 0003).

All fixtures here are hand-constructed byte sequences in the documented
`.bi5` record shape - never real downloaded market data. No network call is
made anywhere in this module.
"""
from __future__ import annotations

import lzma
import struct
from datetime import UTC, datetime, timedelta

import pytest

from maysani_quant.data.providers.base import ArtifactParseError, RawArtifact
from maysani_quant.data.providers.dukascopy import DukascopyProvider, _hour_starts, _url_for

HOUR = datetime(2024, 1, 3, 10, 0, 0, tzinfo=UTC)


def _artifact(content: bytes) -> RawArtifact:
    return RawArtifact(
        provider="dukascopy",
        provider_version="test",
        instrument="EURUSD",
        requested_start=HOUR,
        requested_end=HOUR + timedelta(hours=1),
        retrieved_at=HOUR,
        source_uri="test://fixture",
        content=content,
    )


def _bi5(records: list[tuple[int, int, int, float, float]]) -> bytes:
    raw = b"".join(struct.pack(">Iiiff", *r) for r in records)
    return lzma.compress(raw)


def test_parses_records_with_documented_point_value():
    provider = DukascopyProvider(price_precision=5)
    content = _bi5([(0, 108234, 108220, 1.5, 2.0), (1500, 108240, 108225, 1.0, 1.0)])
    ticks = list(provider.parse_artifact(_artifact(content)))
    assert len(ticks) == 2
    assert ticks[0].bid == pytest.approx(1.08220)
    assert ticks[0].ask == pytest.approx(1.08234)
    assert ticks[0].bid_volume == pytest.approx(2.0)
    assert ticks[0].ask_volume == pytest.approx(1.5)
    assert ticks[0].timestamp == HOUR
    assert ticks[1].timestamp == HOUR + timedelta(milliseconds=1500)


def test_empty_hour_yields_no_ticks_without_error():
    """A genuinely empty artifact (e.g. a weekend hour) is not an error."""
    provider = DukascopyProvider(price_precision=5)
    assert list(provider.parse_artifact(_artifact(b""))) == []


def test_non_lzma_bytes_raise_artifact_parse_error():
    provider = DukascopyProvider(price_precision=5)
    with pytest.raises(ArtifactParseError):
        list(provider.parse_artifact(_artifact(b"not an lzma stream")))


def test_truncated_record_raises_artifact_parse_error():
    provider = DukascopyProvider(price_precision=5)
    raw = struct.pack(">Iiiff", 0, 108234, 108220, 1.0, 1.0)[:-3]  # not a multiple of 20 bytes
    with pytest.raises(ArtifactParseError):
        list(provider.parse_artifact(_artifact(lzma.compress(raw))))


def test_url_uses_zero_indexed_month():
    url = _url_for("EURUSD", datetime(2024, 1, 3, 10, tzinfo=UTC))
    assert "/2024/00/03/10h_ticks.bi5" in url


def test_hour_starts_rejects_naive_datetimes():
    with pytest.raises(ValueError, match="timezone-aware"):
        list(_hour_starts(datetime(2024, 1, 3, 10), datetime(2024, 1, 3, 11)))
