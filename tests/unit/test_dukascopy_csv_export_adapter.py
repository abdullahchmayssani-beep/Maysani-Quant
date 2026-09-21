"""Dukascopy website CSV export adapter tests (ADR 0004).

All fixtures are hand-built, obviously-fake CSV text - never the real
uploaded Dukascopy export. No network call is made anywhere in this module.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from maysani_quant.data.providers.base import ArtifactParseError
from maysani_quant.data.providers.dukascopy_csv_export import DukascopyCsvExportProvider

START = datetime(2024, 1, 3, 12, tzinfo=UTC)
END = START + timedelta(hours=1)

_HEADER = "Etc/UTC,Open,High,Low,Close,Volume\n"


def _write(tmp_path: Path, name: str, rows: list[str]) -> Path:
    path = tmp_path / name
    path.write_text(_HEADER + "\n".join(rows) + "\n", encoding="utf-8")
    return path


def _bid_ask(tmp_path: Path, bid_rows: list[str], ask_rows: list[str]):
    bid_path = _write(tmp_path, "bid.csv", bid_rows)
    ask_path = _write(tmp_path, "ask.csv", ask_rows)
    provider = DukascopyCsvExportProvider(bid_path, ask_path)
    artifacts = list(provider.fetch_artifacts("EURUSD", START, END))
    ticks = list(provider.parse_artifacts(artifacts))
    return artifacts, ticks


def test_fetch_artifacts_labels_bid_and_ask(tmp_path: Path):
    artifacts, _ = _bid_ask(
        tmp_path,
        ["2024-01-03T12:00:00+00:00,1.10000,1.10000,1.10000,1.10000,900000"],
        ["2024-01-03T12:00:00+00:00,1.10010,1.10010,1.10010,1.10010,900000"],
    )
    labels = {a.label for a in artifacts}
    assert labels == {"bid", "ask"}
    assert all(a.requested_start == START and a.requested_end == END for a in artifacts)


def test_valid_pair_produces_ticks(tmp_path: Path):
    _, ticks = _bid_ask(
        tmp_path,
        [
            "2024-01-03T12:00:00+00:00,1.10000,1.10000,1.10000,1.10000,900000",
            "2024-01-03T12:00:01+00:00,1.10002,1.10002,1.10002,1.10002,450000",
        ],
        [
            "2024-01-03T12:00:00+00:00,1.10010,1.10010,1.10010,1.10010,1800000",
            "2024-01-03T12:00:01+00:00,1.10012,1.10012,1.10012,1.10012,900000",
        ],
    )
    assert len(ticks) == 2
    assert ticks[0].bid == pytest.approx(1.10000)
    assert ticks[0].ask == pytest.approx(1.10010)
    assert ticks[0].bid_volume == pytest.approx(900000)
    assert ticks[0].ask_volume == pytest.approx(1800000)
    assert ticks[1].timestamp == START + timedelta(seconds=1)


def test_row_count_mismatch_raises(tmp_path: Path):
    with pytest.raises(ArtifactParseError, match="rows"):
        _bid_ask(
            tmp_path,
            ["2024-01-03T12:00:00+00:00,1.10000,1.10000,1.10000,1.10000,900000"],
            [
                "2024-01-03T12:00:00+00:00,1.10010,1.10010,1.10010,1.10010,900000",
                "2024-01-03T12:00:01+00:00,1.10012,1.10012,1.10012,1.10012,900000",
            ],
        )


def test_row_timestamp_misalignment_raises(tmp_path: Path):
    with pytest.raises(ArtifactParseError, match="pairing is unsafe"):
        _bid_ask(
            tmp_path,
            ["2024-01-03T12:00:00+00:00,1.10000,1.10000,1.10000,1.10000,900000"],
            ["2024-01-03T12:00:01+00:00,1.10010,1.10010,1.10010,1.10010,900000"],
        )


def test_non_ohlc_equal_row_raises(tmp_path: Path):
    """A row that isn't a genuine single tick (O=H=L=C) is rejected, never
    silently averaged or truncated into one."""
    with pytest.raises(ArtifactParseError, match="single-tick row"):
        _bid_ask(
            tmp_path,
            ["2024-01-03T12:00:00+00:00,1.10000,1.10005,1.09995,1.10002,900000"],
            ["2024-01-03T12:00:00+00:00,1.10010,1.10010,1.10010,1.10010,900000"],
        )


def test_naive_timestamp_raises(tmp_path: Path):
    with pytest.raises(ArtifactParseError, match="naive timestamp"):
        _bid_ask(
            tmp_path,
            ["2024-01-03T12:00:00,1.10000,1.10000,1.10000,1.10000,900000"],
            ["2024-01-03T12:00:00+00:00,1.10010,1.10010,1.10010,1.10010,900000"],
        )


def test_wrong_header_raises(tmp_path: Path):
    bid_path = tmp_path / "bid.csv"
    bid_path.write_text("Timestamp,O,H,L,C,V\n2024-01-03T12:00:00+00:00,1,1,1,1,1\n")
    ask_path = _write(
        tmp_path, "ask.csv", ["2024-01-03T12:00:00+00:00,1.1001,1.1001,1.1001,1.1001,900000"]
    )
    provider = DukascopyCsvExportProvider(bid_path, ask_path)
    artifacts = list(provider.fetch_artifacts("EURUSD", START, END))
    with pytest.raises(ArtifactParseError, match="unexpected header"):
        list(provider.parse_artifacts(artifacts))


def test_ask_below_bid_flows_through_to_canonical_validate_as_invalid(tmp_path: Path):
    """PARSE only checks structure/alignment; price plausibility is
    CANONICAL VALIDATE's job (ADR 0003) - an impossible quote must still
    surface, just one stage later."""
    from maysani_quant.data.pipeline.canonical_validate import validate_canonical_bars
    from maysani_quant.data.pipeline.normalize import normalize_ticks_to_bars
    from maysani_quant.domain.enums import QualityFlag

    _, ticks = _bid_ask(
        tmp_path,
        ["2024-01-03T12:00:00+00:00,1.10020,1.10020,1.10020,1.10020,900000"],
        ["2024-01-03T12:00:00+00:00,1.10010,1.10010,1.10010,1.10010,900000"],
    )
    bars = normalize_ticks_to_bars(
        ticks,
        instrument="EURUSD",
        bar_seconds=3600,
        available_time_policy="bar_close",
        available_time_lag_seconds=0,
        source_tag="test",
    )
    report = validate_canonical_bars(bars, expected_bar_seconds=3600, require_bid_ask=True)
    assert not report.ok
    assert any(i.flag is QualityFlag.NEGATIVE_SPREAD for i in report.issues)
