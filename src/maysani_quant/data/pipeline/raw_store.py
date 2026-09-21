"""RAW STORE: immutable, content-addressed cache of provider artifacts.

Bytes are written exactly once per SHA-256 and never rewritten - a second
store of the same content is a no-op verify, not a second write. This is the
only stage allowed to touch the raw cache directory; PARSE reads from it, it
never writes to it.

Also maintains a small **request index** (ADR 0005) mapping
`(provider, instrument, requested_start, requested_end) -> sha256`, so a
provider that already has the exact artifact for a request can skip an
expensive re-fetch (typically a network call) entirely, without needing to
know a content hash in advance. The index is a pointer, not a source of
truth: `find_by_request` always re-verifies the pointed-to blob's checksum
before trusting it, so a corrupted or hand-edited cache entry is treated as
"not cached" rather than silently served.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from maysani_quant.data.provenance import (
    RawManifest,
    atomic_write_bytes,
    atomic_write_text,
    sha256_bytes,
)
from maysani_quant.data.providers.base import RawArtifact


class RawArtifactStore:
    """Local, gitignored, content-addressed cache under `root`.

    Layout: `<root>/<provider>/<instrument>/<sha256[:2]>/<sha256>.bin` plus a
    sidecar `<sha256>.manifest.json`. Content-addressing means a corrupt or
    truncated write can never silently pass as a different, valid artifact.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def _paths(self, provider: str, instrument: str, digest: str) -> tuple[Path, Path]:
        directory = self.root / provider / instrument / digest[:2]
        return directory / f"{digest}.bin", directory / f"{digest}.manifest.json"

    def _request_index_path(
        self,
        provider: str,
        instrument: str,
        requested_start: datetime,
        requested_end: datetime,
        label: str = "",
    ) -> Path:
        """One index entry per (window, label).

        `label` is part of the key because a single requested window can
        legitimately produce more than one artifact - ADR 0004's CSV export
        yields a `bid` and an `ask` file for the same window. Without the
        label the second `put` would overwrite the first's pointer and the
        window would resolve to only one of the two artifacts. An empty
        label (the `.bi5` case, one artifact per window) keys exactly as
        before, so existing cache entries stay valid.
        """
        key = (
            f"{requested_start.astimezone(UTC):%Y%m%dT%H%M%SZ}_"
            f"{requested_end.astimezone(UTC):%Y%m%dT%H%M%SZ}"
        )
        if label:
            key = f"{key}__{label}"
        return self.root / provider / instrument / "_requests" / f"{key}.json"

    def find_by_request(
        self,
        provider: str,
        instrument: str,
        requested_start: datetime,
        requested_end: datetime,
        label: str = "",
    ) -> RawManifest | None:
        """The cache-hit lookup: is there already a verified artifact on disk
        for this exact request? Self-healing - any inconsistency (missing
        index, missing blob, checksum mismatch, corrupt index JSON) is
        treated as a cache miss, never as an error."""
        index_path = self._request_index_path(
            provider, instrument, requested_start, requested_end, label
        )
        try:
            digest = json.loads(index_path.read_text(encoding="utf-8"))["sha256"]
            self.get_bytes(provider, instrument, digest)  # re-verifies checksum
            return self.get_manifest(provider, instrument, digest)
        except (OSError, KeyError, ValueError):
            return None

    def put(self, artifact: RawArtifact) -> RawManifest:
        digest = sha256_bytes(artifact.content)
        blob_path, manifest_path = self._paths(artifact.provider, artifact.instrument, digest)
        manifest = RawManifest(
            sha256=digest,
            provider=artifact.provider,
            provider_version=artifact.provider_version,
            instrument=artifact.instrument,
            requested_start=artifact.requested_start,
            requested_end=artifact.requested_end,
            retrieved_at=artifact.retrieved_at,
            source_uri=artifact.source_uri,
            byte_length=len(artifact.content),
            label=artifact.label,
        )
        if blob_path.exists():
            existing = blob_path.read_bytes()
            if sha256_bytes(existing) != digest:
                raise OSError(
                    f"content-addressed collision at {blob_path}: on-disk bytes do not "
                    "match their own filename hash. Refusing to overwrite. Delete that "
                    "file to let it be re-fetched."
                )
        else:
            atomic_write_bytes(blob_path, artifact.content)

        # Write the manifest whenever it is absent, not only on the path that
        # wrote the blob: a stored blob whose sidecar went missing would
        # otherwise stay permanently un-provenanced AND permanently
        # un-cacheable (find_by_request needs the manifest and would keep
        # missing). The existing sidecar is never overwritten - it records the
        # retrieval that first produced these bytes.
        if not manifest_path.exists():
            atomic_write_text(manifest_path, json.dumps(manifest.to_dict(), indent=2))

        # Always (re)point this exact request at the (possibly pre-existing)
        # blob, so a future identical request is a cache hit even if this
        # call's bytes happened to already be stored under a prior request.
        index_path = self._request_index_path(
            artifact.provider,
            artifact.instrument,
            artifact.requested_start,
            artifact.requested_end,
            artifact.label,
        )
        atomic_write_text(index_path, json.dumps({"sha256": digest}))
        return manifest

    def get_bytes(self, provider: str, instrument: str, digest: str) -> bytes:
        blob_path, _ = self._paths(provider, instrument, digest)
        data = blob_path.read_bytes()
        if sha256_bytes(data) != digest:
            raise OSError(f"stored artifact at {blob_path} does not match its content hash")
        return data

    def get_manifest(self, provider: str, instrument: str, digest: str) -> RawManifest:
        _, manifest_path = self._paths(provider, instrument, digest)
        return RawManifest.from_dict(json.loads(manifest_path.read_text(encoding="utf-8")))
