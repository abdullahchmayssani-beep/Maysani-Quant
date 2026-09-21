"""Raw-artifact validation: retrieval and structural integrity only.

Deliberately separate from `canonical_validate.py` (correction: the two must
not be mixed). This module never looks at prices, timestamps-as-data, bid/ask
or spreads - it only asks "is this artifact the bytes we think it is, and can
it be decompressed/parsed at all". A checksum mismatch or truncated/corrupt
artifact is a hard failure, never a flag.
"""
from __future__ import annotations

from dataclasses import dataclass

from maysani_quant.data.provenance import RawManifest, sha256_bytes
from maysani_quant.data.providers.base import ArtifactParseError


class RawArtifactInvalid(RuntimeError):
    """The stored artifact fails a structural or checksum check."""


@dataclass(frozen=True)
class RawValidationResult:
    sha256: str
    byte_length: int
    checksum_ok: bool
    non_empty: bool

    @property
    def ok(self) -> bool:
        """A zero-byte artifact is valid (e.g. an hour with no ticks over a
        weekend close); only a checksum mismatch is a hard failure."""
        return self.checksum_ok


def validate_raw_artifact(content: bytes, manifest: RawManifest) -> RawValidationResult:
    """Checksum check. Raises if the manifest and bytes disagree."""
    digest = sha256_bytes(content)
    result = RawValidationResult(
        sha256=digest,
        byte_length=len(content),
        checksum_ok=(digest == manifest.sha256),
        non_empty=len(content) > 0,
    )
    if not result.checksum_ok:
        raise RawArtifactInvalid(
            f"checksum mismatch: manifest says {manifest.sha256}, bytes hash to {digest}"
        )
    return result


def require_parseable(ticks_iter, artifact_uri: str) -> list:
    """Materialize a provider's PARSE iterator, converting any parse failure
    into a clearly-attributed error rather than letting a partial/garbled
    tick list flow silently into NORMALIZE."""
    try:
        return list(ticks_iter)
    except Exception as exc:  # noqa: BLE001 - re-raised with artifact context
        raise ArtifactParseError(f"failed to parse artifact {artifact_uri}: {exc}") from exc
