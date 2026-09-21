"""Dukascopy website "Historical Data Feed" CSV export (ADR 0004).

This is a **different ingestion path** from `dukascopy.py`'s `.bi5` adapter,
not a variant of it: the website's per-tick CSV export gives BID and ASK as
two independent single-sided files, at 1-second timestamp resolution
(`.bi5` has millisecond resolution and both sides in one record). Only this
module is allowed to know that column layout and the row-pairing policy
below.

## Column layout (observed on a real sample, not officially documented)

```
Etc/UTC,Open,High,Low,Close,Volume
2026-09-17T12:00:00+00:00,1.14733,1.14733,1.14733,1.14733,1800000
```

`Open == High == Low == Close` on every row (each row is one tick, not an
aggregated bar - the export tool reuses OHLC column headers for a
single-tick "bar"). This adapter uses `Close`. `Volume` looks like the
provider's per-tick volume in raw currency units (1_800_000 == 1.8 "million"
in Dukascopy's commonly documented volume convention) but that scaling is
**not applied here** - `[UNVERIFIED]`, passed through as reported.

## Row-pairing policy (ADR 0004)

The BID and ASK files are paired **by row index**, after verifying (not
assuming) that both files have the same row count and identical per-row
timestamps. On the real 2026-09-17 12:00-13:00Z EUR/USD sample (5293 rows
each side) this holds at every row, and pairing this way yields `ask >= bid`
at all 5293 rows with a realistic 1-4 pip spread distribution - strong
corroborating evidence, not a Dukascopy-documented guarantee. If either
check fails on a different file, this adapter raises `ArtifactParseError`
rather than falling back to a timestamp-based join that could silently
mispair same-second ticks.
"""
from __future__ import annotations

import csv
import io
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path

from maysani_quant.data.providers.base import ArtifactParseError, ProviderTick, RawArtifact

PROVIDER_NAME = "dukascopy_csv_export"
PROVIDER_VERSION = "1.0.0-unverified"

_EXPECTED_HEADER = ["Etc/UTC", "Open", "High", "Low", "Close", "Volume"]


def _parse_rows(content: bytes, source_uri: str) -> list[tuple[datetime, float, float]]:
    """Returns (timestamp, price, volume) per row. Raises on malformed rows -
    never silently drops or repairs one."""
    text = content.decode("utf-8-sig")
    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration as exc:
        raise ArtifactParseError(f"{source_uri}: empty file, no header row") from exc
    if header != _EXPECTED_HEADER:
        raise ArtifactParseError(
            f"{source_uri}: unexpected header {header!r}, expected {_EXPECTED_HEADER!r}"
        )
    rows: list[tuple[datetime, float, float]] = []
    for line_no, row in enumerate(reader, start=2):
        if len(row) != len(_EXPECTED_HEADER):
            raise ArtifactParseError(f"{source_uri}:{line_no}: expected 6 columns, got {row!r}")
        ts_text, open_, high, low, close, volume = row
        try:
            ts = datetime.fromisoformat(ts_text)
            o, h, low_v, c, vol = float(open_), float(high), float(low), float(close), float(volume)
        except ValueError as exc:
            raise ArtifactParseError(f"{source_uri}:{line_no}: malformed row {row!r}: {exc}") from exc
        if ts.tzinfo is None:
            raise ArtifactParseError(f"{source_uri}:{line_no}: naive timestamp {ts_text!r}")
        if not (o == h == low_v == c):
            raise ArtifactParseError(
                f"{source_uri}:{line_no}: expected a single-tick row (O=H=L=C), got "
                f"O={o} H={h} L={low_v} C={c}"
            )
        rows.append((ts.astimezone(UTC), c, vol))
    return rows


class DukascopyCsvExportProvider:
    """FETCH reads two local files (already downloaded by hand from
    Dukascopy's website); PARSE pairs them by validated row index.

    This is a legitimate FETCH implementation, not a bypass of RAW STORE:
    the files' bytes are still written to the immutable raw cache, verbatim,
    before PARSE ever runs (see `MarketDataService._run_pipeline`).
    """

    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self, bid_path: str | Path, ask_path: str | Path) -> None:
        self.bid_path = Path(bid_path)
        self.ask_path = Path(ask_path)

    def fetch_artifacts(
        self, instrument: str, start: datetime, end: datetime
    ) -> Iterator[RawArtifact]:
        retrieved_at = datetime.now(UTC)
        for label, path in (("bid", self.bid_path), ("ask", self.ask_path)):
            yield RawArtifact(
                provider=self.provider_name,
                provider_version=self.provider_version,
                instrument=instrument,
                requested_start=start,
                requested_end=end,
                retrieved_at=retrieved_at,
                source_uri=f"file://{path}",
                content=path.read_bytes(),
                label=label,
            )

    def parse_artifacts(self, group: Sequence[RawArtifact]) -> Iterator[ProviderTick]:
        by_label = {a.label: a for a in group}
        if set(by_label) != {"bid", "ask"}:
            raise ArtifactParseError(
                f"expected exactly one 'bid' and one 'ask' artifact in the group, "
                f"got labels {sorted(by_label)}"
            )
        bid_artifact, ask_artifact = by_label["bid"], by_label["ask"]
        bid_rows = _parse_rows(bid_artifact.content, bid_artifact.source_uri)
        ask_rows = _parse_rows(ask_artifact.content, ask_artifact.source_uri)

        if len(bid_rows) != len(ask_rows):
            raise ArtifactParseError(
                f"BID has {len(bid_rows)} rows but ASK has {len(ask_rows)} rows - "
                "cannot pair by row index without a matching count"
            )
        for i, ((bid_ts, bid_px, bid_vol), (ask_ts, ask_px, ask_vol)) in enumerate(
            zip(bid_rows, ask_rows, strict=True)
        ):
            if bid_ts != ask_ts:
                raise ArtifactParseError(
                    f"row {i}: BID timestamp {bid_ts.isoformat()} != "
                    f"ASK timestamp {ask_ts.isoformat()} - row-index pairing is unsafe"
                )
            yield ProviderTick(
                instrument=bid_artifact.instrument,
                timestamp=bid_ts,
                bid=bid_px,
                ask=ask_px,
                bid_volume=bid_vol,
                ask_volume=ask_vol,
            )
