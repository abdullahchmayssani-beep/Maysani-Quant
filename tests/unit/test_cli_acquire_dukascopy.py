"""CLI wiring test for `acquire-dukascopy` (ADR 0005).

Patches `urllib.request.urlopen` itself (the one real socket call, made
inside `DukascopyProvider`'s default opener) rather than anything CLI- or
provider-internal, so this test exercises the exact code path a real
invocation would use, fully offline.
"""
from __future__ import annotations

import io
import lzma
import struct
import urllib.request
from pathlib import Path

import pytest

from maysani_quant.cli import main

GOOD_BYTES = lzma.compress(struct.pack(">Iiiff", 0, 108234, 108220, 1.0, 1.0))


class _FakeResponse:
    def __init__(self, content: bytes) -> None:
        self._buf = io.BytesIO(content)

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc) -> None:
        return None

    def read(self) -> bytes:
        return self._buf.read()


def test_acquire_dukascopy_end_to_end_via_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: _FakeResponse(GOOD_BYTES))

    exit_code = main(
        [
            "acquire-dukascopy",
            "--instrument", "EURUSD",
            "--start", "2024-01-03T10:00:00Z",
            "--end", "2024-01-03T11:00:00Z",
            "--raw-root", str(tmp_path / "raw"),
            "--canonical-root", str(tmp_path / "canonical"),
            "--no-require-bid-ask",
        ]
    )
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "artifacts requested: 1" in out
    assert "downloaded         : 1" in out
    assert "cache hits         : 0" in out
    assert "canonical identity :" in out
    assert "quality status     : 1 bars, no issues (VALID)" in out

    # Re-running the identical command must be a pure cache hit.
    exit_code2 = main(
        [
            "acquire-dukascopy",
            "--instrument", "EURUSD",
            "--start", "2024-01-03T10:00:00Z",
            "--end", "2024-01-03T11:00:00Z",
            "--raw-root", str(tmp_path / "raw"),
            "--canonical-root", str(tmp_path / "canonical"),
            "--no-require-bid-ask",
        ]
    )
    out2 = capsys.readouterr().out
    assert exit_code2 == 0
    assert "cache hits         : 1" in out2
    assert "downloaded         : 0" in out2


def test_acquire_dukascopy_rejects_end_before_start(tmp_path: Path, capsys):
    exit_code = main(
        [
            "acquire-dukascopy",
            "--start", "2024-01-03T11:00:00Z",
            "--end", "2024-01-03T10:00:00Z",
            "--raw-root", str(tmp_path / "raw"),
            "--canonical-root", str(tmp_path / "canonical"),
        ]
    )
    assert exit_code == 2
