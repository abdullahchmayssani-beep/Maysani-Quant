"""MarketDataService: the provider-independent facade (ADR 0003).

Runs FETCH -> RAW STORE -> PARSE -> NORMALIZE -> CANONICAL VALIDATE ->
CANONICAL STORE for one `MarketDataProvider` and exposes the same surface
`CsvMarketDataSource` exposes, so `backtest/runner.py` and `cli.py` need no
provider-specific branching beyond *constructing* the right source.
"""
from __future__ import annotations

from collections.abc import Iterator, Sequence
from datetime import datetime
from pathlib import Path

from maysani_quant.data.pipeline.canonical_store import CanonicalStore, now_utc
from maysani_quant.data.pipeline.canonical_validate import (
    CanonicalValidationReport,
    validate_canonical_bars,
)
from maysani_quant.data.pipeline.normalize import normalize_ticks_to_bars
from maysani_quant.data.pipeline.raw_store import RawArtifactStore
from maysani_quant.data.pipeline.raw_validate import require_parseable, validate_raw_artifact
from maysani_quant.data.provenance import (
    SCHEMA_VERSION,
    CanonicalManifest,
    NormalizationPolicy,
    canonical_identity_hash,
)
from maysani_quant.data.providers.base import MarketDataProvider, RawArtifact
from maysani_quant.domain.models import MarketBar

PIPELINE_VERSION = "pipeline-v1"


class MarketDataService:
    """A `MarketDataSource`-compatible facade backed by a `MarketDataProvider`.

    Every run of the pipeline re-fetches artifacts over the network (raw
    storage is content-addressed and idempotent, but there is no
    (provider, instrument, hour) index yet to skip a re-fetch before
    downloading - a documented V0.2 limitation, not a correctness gap).
    """

    def __init__(
        self,
        provider: MarketDataProvider,
        *,
        instrument: str,
        start: datetime,
        end: datetime,
        bar_seconds: int,
        timeframe: str,
        available_time_policy: str = "bar_close",
        available_time_lag_seconds: int = 0,
        raw_root: str | Path = "data/raw",
        canonical_root: str | Path = "data/cache/canonical",
        require_bid_ask: bool = True,
    ) -> None:
        self.provider = provider
        self.instrument = instrument
        self.start = start
        self.end = end
        self.bar_seconds = bar_seconds
        self.price_kind = "bidask"
        self.available_time_policy = available_time_policy
        self.is_synthetic = False

        self._raw_store = RawArtifactStore(raw_root)
        self._canonical_store = CanonicalStore(canonical_root)
        self._policy = NormalizationPolicy(
            timeframe=timeframe,
            available_time_policy=available_time_policy,
            available_time_lag_seconds=available_time_lag_seconds,
            ohlc_price_kind="midpoint",
        )

        self._bars, self.manifest = self._run_pipeline(require_bid_ask)
        self.validation: CanonicalValidationReport = validate_canonical_bars(
            self._bars, expected_bar_seconds=bar_seconds, require_bid_ask=require_bid_ask
        )

    def _run_pipeline(
        self, require_bid_ask: bool
    ) -> tuple[tuple[MarketBar, ...], CanonicalManifest]:
        raw_hashes: list[str] = []
        groups: dict[tuple[datetime, datetime], list[RawArtifact]] = {}
        group_order: list[tuple[datetime, datetime]] = []
        for artifact in self.provider.fetch_artifacts(self.instrument, self.start, self.end):
            # RAW STORE happens before PARSE ever sees the bytes.
            raw_manifest = self._raw_store.put(artifact)
            stored = self._raw_store.get_bytes(
                artifact.provider, artifact.instrument, raw_manifest.sha256
            )
            validate_raw_artifact(stored, raw_manifest)
            raw_hashes.append(raw_manifest.sha256)

            # PARSE operates on a group of artifacts sharing one requested
            # window (ADR 0004) - a `.bi5` hour is a group of one; a website
            # CSV export's separate BID/ASK files land in the same group.
            key = (artifact.requested_start, artifact.requested_end)
            if key not in groups:
                groups[key] = []
                group_order.append(key)
            groups[key].append(artifact)

        all_ticks = []
        for key in group_order:
            group = groups[key]
            ticks = require_parseable(
                self.provider.parse_artifacts(group),
                ",".join(a.source_uri for a in group),
            )
            all_ticks.extend(ticks)

        identity_hash = canonical_identity_hash(
            raw_artifact_hashes=raw_hashes,
            provider=self.provider.provider_name,
            provider_version=self.provider.provider_version,
            instrument=self.instrument,
            requested_start=self.start,
            requested_end=self.end,
            schema_version=SCHEMA_VERSION,
            normalization_policy=self._policy,
        )

        if self._canonical_store.exists(self.provider.provider_name, self.instrument, identity_hash):
            manifest = self._canonical_store.read_manifest(
                self.provider.provider_name, self.instrument, identity_hash
            )
            bars = tuple(
                self._canonical_store.read_bars(
                    self.provider.provider_name, self.instrument, identity_hash
                )
            )
            return bars, manifest

        source_tag = f"{self.provider.provider_name}:{identity_hash[:12]}"
        bars = tuple(
            normalize_ticks_to_bars(
                all_ticks,
                instrument=self.instrument,
                bar_seconds=self.bar_seconds,
                available_time_policy=self._policy.available_time_policy,
                available_time_lag_seconds=self._policy.available_time_lag_seconds,
                source_tag=source_tag,
            )
        )
        validation = validate_canonical_bars(
            bars, expected_bar_seconds=self.bar_seconds, require_bid_ask=require_bid_ask
        )
        manifest = CanonicalManifest(
            canonical_identity_hash=identity_hash,
            raw_artifact_hashes=tuple(raw_hashes),
            provider=self.provider.provider_name,
            provider_version=self.provider.provider_version,
            instrument=self.instrument,
            requested_start=self.start,
            requested_end=self.end,
            schema_version=SCHEMA_VERSION,
            normalization_policy=self._policy,
            pipeline_version=PIPELINE_VERSION,
            retrieved_at=now_utc(),
            bar_count=len(bars),
            actual_start=bars[0].end_time if bars else None,
            actual_end=bars[-1].end_time if bars else None,
            validation_summary={"severity": validation.severity.value, **validation.counts()},
        )
        self._canonical_store.write(manifest, bars)
        return bars, manifest

    # -- MarketDataSource-compatible surface -------------------------------

    @property
    def dataset_path(self) -> str:
        bars_path, _ = self._canonical_store.paths_for(
            self.provider.provider_name, self.instrument, self.manifest.canonical_identity_hash
        )
        return str(bars_path)

    @property
    def data_hash(self) -> str:
        return self.manifest.canonical_identity_hash

    @property
    def file_hash(self) -> str:
        """No single 'file' underlies a multi-artifact fetch; the closest
        equivalent traceability handle is the canonical identity hash."""
        return self.manifest.canonical_identity_hash

    def all_bars(self) -> Sequence[MarketBar]:
        return self._bars

    def iter_events(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> Iterator[MarketBar]:
        for bar in self._bars:
            if start is not None and bar.end_time < start:
                continue
            if end is not None and bar.end_time > end:
                continue
            yield bar
