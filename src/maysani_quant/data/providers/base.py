"""The provider contract (ADR 0003).

`MarketDataProvider` is deliberately two methods, not one, so that FETCH can
be immutably stored before PARSE ever runs (see `data/pipeline/raw_store.py`).
A provider never emits a `MarketBar` - that is NORMALIZE's job, done by
provider-agnostic code in `data/pipeline/normalize.py`. A provider emits
`RawArtifact` (its native bytes) from `fetch_artifacts`, and `ProviderTick`
(a small, provider-agnostic tick shape) from `parse_artifact`.
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class RawArtifact:
    """One provider-native artifact, exactly as retrieved.

    `content` is the original bytes - compressed, provider-specific,
    unparsed. Nothing may mutate or "clean up" it; RAW STORE persists exactly
    this before PARSE is allowed to run.
    """

    provider: str
    provider_version: str
    instrument: str
    requested_start: datetime
    requested_end: datetime
    retrieved_at: datetime
    source_uri: str
    content: bytes


@dataclass(frozen=True)
class ProviderTick:
    """The one provider-agnostic shape every adapter's PARSE step must
    produce. Unit/scale conversion (e.g. a provider's integer point value)
    happens inside `parse_artifact`, never downstream of it."""

    instrument: str
    timestamp: datetime
    bid: float
    ask: float
    bid_volume: float
    ask_volume: float


class MarketDataProvider(Protocol):
    provider_name: str
    provider_version: str

    def fetch_artifacts(
        self, instrument: str, start: datetime, end: datetime
    ) -> Iterator[RawArtifact]:  # pragma: no cover - protocol
        """FETCH. Retrieves native artifacts covering [start, end)."""
        ...

    def parse_artifact(
        self, artifact: RawArtifact
    ) -> Iterator[ProviderTick]:  # pragma: no cover - protocol
        """PARSE. Turns one stored artifact's bytes into ticks."""
        ...


class ArtifactRetrievalError(RuntimeError):
    """FETCH failed. Never silently substituted with cached or fabricated data."""


class ArtifactParseError(RuntimeError):
    """PARSE failed on structurally invalid or unexpected bytes."""
