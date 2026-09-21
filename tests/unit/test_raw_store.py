"""RAW STORE tests: content-addressed, immutable artifact cache (ADR 0003)."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from maysani_quant.data.pipeline.raw_store import RawArtifactStore
from maysani_quant.data.pipeline.raw_validate import RawArtifactInvalid, validate_raw_artifact
from maysani_quant.data.providers.base import RawArtifact

HOUR = datetime(2024, 1, 3, 10, tzinfo=UTC)


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


def test_put_then_get_roundtrips_bytes_and_manifest(tmp_path: Path):
    store = RawArtifactStore(tmp_path)
    manifest = store.put(_artifact(b"hello world"))
    assert manifest.byte_length == len(b"hello world")
    assert manifest.provider == "dukascopy"

    fetched = store.get_bytes("dukascopy", "EURUSD", manifest.sha256)
    assert fetched == b"hello world"

    fetched_manifest = store.get_manifest("dukascopy", "EURUSD", manifest.sha256)
    assert fetched_manifest.sha256 == manifest.sha256
    assert fetched_manifest.requested_start == HOUR


def test_identical_bytes_are_not_rewritten(tmp_path: Path):
    store = RawArtifactStore(tmp_path)
    m1 = store.put(_artifact(b"same bytes"))
    blob_path, _ = store._paths("dukascopy", "EURUSD", m1.sha256)
    original_mtime = blob_path.stat().st_mtime_ns

    m2 = store.put(_artifact(b"same bytes"))
    assert m2.sha256 == m1.sha256
    assert blob_path.stat().st_mtime_ns == original_mtime, "identical content must not be rewritten"


def test_different_bytes_get_different_content_addresses(tmp_path: Path):
    store = RawArtifactStore(tmp_path)
    m1 = store.put(_artifact(b"artifact one"))
    m2 = store.put(_artifact(b"artifact two"))
    assert m1.sha256 != m2.sha256


def test_validate_raw_artifact_detects_checksum_mismatch(tmp_path: Path):
    store = RawArtifactStore(tmp_path)
    manifest = store.put(_artifact(b"trustworthy bytes"))
    with pytest.raises(RawArtifactInvalid):
        validate_raw_artifact(b"tampered bytes", manifest)


def test_validate_raw_artifact_accepts_empty_content(tmp_path: Path):
    """An empty artifact (e.g. a weekend hour with no ticks) is valid."""
    store = RawArtifactStore(tmp_path)
    manifest = store.put(_artifact(b""))
    result = validate_raw_artifact(b"", manifest)
    assert result.ok
    assert not result.non_empty
