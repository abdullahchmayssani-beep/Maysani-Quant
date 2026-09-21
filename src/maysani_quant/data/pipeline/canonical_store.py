"""CANONICAL STORE: local, gitignored cache of validated, normalized bars.

Keyed by `canonical_identity_hash` (ADR 0003 s.7), so re-running the same raw
bytes through the same pipeline lands on the same cache entry instead of
writing a duplicate. The manifest is the source of truth for provenance; the
CSV alongside it is a plain, inspectable rendering of the bars themselves.
"""
from __future__ import annotations

import csv
import io
import json
from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from maysani_quant.data.provenance import (
    CanonicalManifest,
    NormalizationPolicy,
    atomic_write_bytes,
    atomic_write_text,
    sha256_bytes,
)
from maysani_quant.domain.enums import QualityFlag
from maysani_quant.domain.models import MarketBar


class CanonicalIntegrityError(OSError):
    """The cached bars file no longer matches the checksum its manifest
    recorded. Never repaired and never silently served - an experiment that
    cites this dataset identity would otherwise be citing different bars."""

_COLUMNS = [
    "start_time", "end_time", "available_time", "open", "high", "low", "close",
    "volume", "bid_close", "ask_close", "spread", "source", "quality_flags",
]


class CanonicalStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def paths_for(self, provider: str, instrument: str, identity_hash: str) -> tuple[Path, Path]:
        directory = self.root / provider / instrument
        return directory / f"{identity_hash}.csv", directory / f"{identity_hash}.manifest.json"

    def exists(self, provider: str, instrument: str, identity_hash: str) -> bool:
        bars_path, manifest_path = self.paths_for(provider, instrument, identity_hash)
        return bars_path.exists() and manifest_path.exists()

    def write(self, manifest: CanonicalManifest, bars: Sequence[MarketBar]) -> CanonicalManifest:
        """Writes the bars first, then the manifest that checksums them.

        Order matters: `exists()` requires both, so an interrupted write
        leaves an incomplete entry that is simply recomputed next time rather
        than served."""
        bars_path, manifest_path = self.paths_for(
            manifest.provider, manifest.instrument, manifest.canonical_identity_hash
        )
        buffer = io.StringIO(newline="")
        writer = csv.writer(buffer)
        writer.writerow(_COLUMNS)
        for bar in bars:
            writer.writerow(
                [
                    bar.start_time.isoformat(),
                    bar.end_time.isoformat(),
                    bar.available_time.isoformat(),
                    bar.open, bar.high, bar.low, bar.close,
                    "" if bar.volume is None else bar.volume,
                    "" if bar.bid_close is None else bar.bid_close,
                    "" if bar.ask_close is None else bar.ask_close,
                    "" if bar.spread is None else bar.spread,
                    bar.source,
                    ";".join(f.value for f in bar.quality_flags),
                ]
            )
        payload = buffer.getvalue().encode("utf-8")
        stamped = replace(manifest, bars_sha256=sha256_bytes(payload))
        atomic_write_bytes(bars_path, payload)
        atomic_write_text(manifest_path, json.dumps(stamped.to_dict(), indent=2))
        return stamped

    def read_manifest(self, provider: str, instrument: str, identity_hash: str) -> CanonicalManifest:
        _, manifest_path = self.paths_for(provider, instrument, identity_hash)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        policy = data["normalization_policy"]
        return CanonicalManifest(
            canonical_identity_hash=data["canonical_identity_hash"],
            raw_artifact_hashes=tuple(data["raw_artifact_hashes"]),
            provider=data["provider"],
            provider_version=data["provider_version"],
            instrument=data["instrument"],
            requested_start=datetime.fromisoformat(data["requested_start"]),
            requested_end=datetime.fromisoformat(data["requested_end"]),
            schema_version=data["schema_version"],
            normalization_policy=NormalizationPolicy(**policy),
            pipeline_version=data["pipeline_version"],
            retrieved_at=datetime.fromisoformat(data["retrieved_at"]),
            bar_count=data["bar_count"],
            actual_start=datetime.fromisoformat(data["actual_start"]) if data["actual_start"] else None,
            actual_end=datetime.fromisoformat(data["actual_end"]) if data["actual_end"] else None,
            validation_summary=data["validation_summary"],
            bars_sha256=data.get("bars_sha256", ""),
        )

    def read_bars(self, provider: str, instrument: str, identity_hash: str) -> list[MarketBar]:
        bars_path, _ = self.paths_for(provider, instrument, identity_hash)
        payload = bars_path.read_bytes()
        expected = self.read_manifest(provider, instrument, identity_hash).bars_sha256
        if expected and sha256_bytes(payload) != expected:
            raise CanonicalIntegrityError(
                f"cached bars at {bars_path} do not match the bars_sha256 their manifest "
                f"records ({expected[:12]}...). Refusing to serve them under an identity "
                "that no longer describes them; delete the entry to rebuild it."
            )
        bars: list[MarketBar] = []
        with io.StringIO(payload.decode("utf-8"), newline="") as handle:
            for row in csv.DictReader(handle):
                flags = tuple(
                    QualityFlag(f) for f in row["quality_flags"].split(";") if f
                ) or (QualityFlag.OK,)
                bars.append(
                    MarketBar(
                        instrument=instrument,
                        start_time=datetime.fromisoformat(row["start_time"]),
                        end_time=datetime.fromisoformat(row["end_time"]),
                        available_time=datetime.fromisoformat(row["available_time"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]) if row["volume"] else None,
                        bid_close=float(row["bid_close"]) if row["bid_close"] else None,
                        ask_close=float(row["ask_close"]) if row["ask_close"] else None,
                        spread=float(row["spread"]) if row["spread"] else None,
                        source=row["source"],
                        quality_flags=flags,
                    )
                )
        return bars


def now_utc() -> datetime:
    return datetime.now(UTC)
