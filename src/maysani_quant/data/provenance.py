"""Provenance types shared by the raw and canonical caches (ADR 0003).

Two manifests, two different reproducibility contracts:

- `RawManifest` records what was actually retrieved and when. Retrieval time
  is provenance, not identity: two fetches of the same bytes are the same
  artifact.
- `CanonicalManifest` records what the pipeline produced from a set of raw
  artifacts. Its `canonical_identity_hash` depends only on immutable inputs
  (raw hashes, provider, instrument, window, schema/policy version) so that
  running the same raw bytes through the same pipeline reproduces the same
  identity - retrieval time is excluded from that hash on purpose.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime

from maysani_quant.domain.models import stable_hash

SCHEMA_VERSION = "canonical-v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class RawManifest:
    """Everything about one immutably-stored raw provider artifact."""

    sha256: str
    provider: str
    provider_version: str
    instrument: str
    requested_start: datetime
    requested_end: datetime
    retrieved_at: datetime
    source_uri: str
    byte_length: int
    label: str = ""

    def to_dict(self) -> dict:
        return {
            "sha256": self.sha256,
            "provider": self.provider,
            "provider_version": self.provider_version,
            "instrument": self.instrument,
            "requested_start": self.requested_start.isoformat(),
            "requested_end": self.requested_end.isoformat(),
            "retrieved_at": self.retrieved_at.isoformat(),
            "source_uri": self.source_uri,
            "byte_length": self.byte_length,
            "label": self.label,
        }

    @staticmethod
    def from_dict(data: dict) -> RawManifest:
        return RawManifest(
            sha256=data["sha256"],
            provider=data["provider"],
            provider_version=data["provider_version"],
            instrument=data["instrument"],
            requested_start=datetime.fromisoformat(data["requested_start"]),
            requested_end=datetime.fromisoformat(data["requested_end"]),
            retrieved_at=datetime.fromisoformat(data["retrieved_at"]),
            source_uri=data["source_uri"],
            byte_length=int(data["byte_length"]),
            label=data.get("label", ""),
        )


@dataclass(frozen=True)
class NormalizationPolicy:
    """The documented, non-invented policy applied during NORMALIZE.

    Every field here changes the canonical identity hash if changed - see
    ADR 0003 s.4/s.7. `available_time_policy` mirrors the vocabulary V0.1's
    CSV loader already uses (`bar_close` / `bar_close_plus_lag`).
    """

    timeframe: str
    available_time_policy: str
    available_time_lag_seconds: int
    ohlc_price_kind: str  # "midpoint" - see ADR 0003 s.4

    def to_dict(self) -> dict:
        return {
            "timeframe": self.timeframe,
            "available_time_policy": self.available_time_policy,
            "available_time_lag_seconds": self.available_time_lag_seconds,
            "ohlc_price_kind": self.ohlc_price_kind,
        }


@dataclass(frozen=True)
class CanonicalManifest:
    canonical_identity_hash: str
    raw_artifact_hashes: tuple[str, ...]
    provider: str
    provider_version: str
    instrument: str
    requested_start: datetime
    requested_end: datetime
    schema_version: str
    normalization_policy: NormalizationPolicy
    pipeline_version: str
    retrieved_at: datetime = field(compare=False)
    bar_count: int = 0
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    validation_summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "canonical_identity_hash": self.canonical_identity_hash,
            "raw_artifact_hashes": list(self.raw_artifact_hashes),
            "provider": self.provider,
            "provider_version": self.provider_version,
            "instrument": self.instrument,
            "requested_start": self.requested_start.isoformat(),
            "requested_end": self.requested_end.isoformat(),
            "schema_version": self.schema_version,
            "normalization_policy": self.normalization_policy.to_dict(),
            "pipeline_version": self.pipeline_version,
            "retrieved_at": self.retrieved_at.isoformat(),
            "bar_count": self.bar_count,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
            "validation_summary": self.validation_summary,
        }


def canonical_identity_hash(
    *,
    raw_artifact_hashes: list[str],
    provider: str,
    provider_version: str,
    instrument: str,
    requested_start: datetime,
    requested_end: datetime,
    schema_version: str,
    normalization_policy: NormalizationPolicy,
) -> str:
    """Deterministic identity. Retrieval time is deliberately excluded."""
    payload = {
        "raw_artifact_hashes": sorted(raw_artifact_hashes),
        "provider": provider,
        "provider_version": provider_version,
        "instrument": instrument,
        "requested_start": requested_start.isoformat(),
        "requested_end": requested_end.isoformat(),
        "schema_version": schema_version,
        "normalization_policy": normalization_policy.to_dict(),
    }
    return stable_hash(payload)
