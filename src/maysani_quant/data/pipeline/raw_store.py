"""RAW STORE: immutable, content-addressed cache of provider artifacts.

Bytes are written exactly once per SHA-256 and never rewritten - a second
store of the same content is a no-op verify, not a second write. This is the
only stage allowed to touch the raw cache directory; PARSE reads from it, it
never writes to it.
"""
from __future__ import annotations

import json
from pathlib import Path

from maysani_quant.data.provenance import RawManifest, sha256_bytes
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
                    "match their own filename hash. Refusing to overwrite."
                )
            return manifest  # identical bytes already stored; nothing to do
        blob_path.parent.mkdir(parents=True, exist_ok=True)
        blob_path.write_bytes(artifact.content)
        manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
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
