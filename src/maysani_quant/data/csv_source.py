"""CSV market data source.

Two things this module refuses to do quietly:

1. It will not invent an `available_time`. Either the file has the column, or
   the config states a policy (`bar_close` / `bar_close_plus_lag`) and the
   policy is recorded in the dataset fingerprint.
2. It will not treat midpoint OHLC as executable. If `price_kind` is
   `midpoint`, the cost model must supply a spread scenario; the flag travels
   with the dataset so the report can say so.
"""
from __future__ import annotations

import csv
import hashlib
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

from maysani_quant.data.validation import ValidationReport, validate_bars
from maysani_quant.domain.enums import QualityFlag
from maysani_quant.domain.models import MarketBar

SYNTHETIC_MARKER = "SYNTHETIC"


def _parse_timestamp(raw: str) -> datetime:
    text = raw.strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _optional_float(row: dict[str, str], key: str) -> float | None:
    value = row.get(key)
    if value is None or value.strip() == "":
        return None
    return float(value)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


class CsvMarketDataSource:
    """Loads bars eagerly (V0.1 datasets are small) and fingerprints the file."""

    def __init__(
        self,
        path: str | Path,
        instrument: str,
        timeframe: str,
        timestamp_column: str = "timestamp",
        available_time_policy: str = "bar_close",
        available_time_lag_seconds: int = 0,
        price_kind: str = "midpoint",
        bar_duration_seconds: int | None = None,
    ) -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(
                f"dataset not found: {self.path}. V0.1 ships no market data; see data/README.md"
            )
        self.instrument = instrument
        self.timeframe = timeframe
        self.timestamp_column = timestamp_column
        self.available_time_policy = available_time_policy
        self.available_time_lag_seconds = available_time_lag_seconds
        self.price_kind = price_kind
        self.bar_duration_seconds = bar_duration_seconds
        self.file_hash = file_sha256(self.path)
        self._bars: tuple[MarketBar, ...] = tuple(self._load())
        self.validation: ValidationReport = validate_bars(self._bars)

    @property
    def dataset_path(self) -> str:
        return str(self.path)

    @property
    def data_hash(self) -> str:
        """Fingerprint of file content AND the timing policy applied to it.

        Two runs over the same bytes but a different available_time policy are
        NOT the same experiment, so they must not share a data hash.
        """
        material = ":".join(
            [
                self.file_hash,
                self.instrument,
                self.timeframe,
                self.available_time_policy,
                str(self.available_time_lag_seconds),
                self.price_kind,
            ]
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    @property
    def is_synthetic(self) -> bool:
        return SYNTHETIC_MARKER.lower() in self.path.name.lower()

    def _resolve_available_time(self, end_time: datetime, row: dict[str, str]) -> datetime:
        explicit = row.get("available_time")
        if explicit and explicit.strip():
            return _parse_timestamp(explicit)
        if self.available_time_policy == "bar_close":
            return end_time
        if self.available_time_policy == "bar_close_plus_lag":
            return end_time + timedelta(seconds=self.available_time_lag_seconds)
        raise ValueError(f"unknown available_time_policy: {self.available_time_policy}")

    def _load(self) -> Iterator[MarketBar]:
        synthetic = self.is_synthetic
        with self.path.open(newline="", encoding="utf-8") as handle:
            rows = [r for r in csv.DictReader(handle) if r.get(self.timestamp_column)]
        prev_end: datetime | None = None
        for row in rows:
            start_time = _parse_timestamp(row[self.timestamp_column])
            if row.get("end_time"):
                end_time = _parse_timestamp(row["end_time"])
            elif self.bar_duration_seconds:
                end_time = start_time + timedelta(seconds=self.bar_duration_seconds)
            else:
                end_time = start_time
            flags: list[QualityFlag] = []
            if synthetic:
                flags.append(QualityFlag.SYNTHETIC)
            if prev_end is not None and end_time <= prev_end:
                flags.append(QualityFlag.OUT_OF_ORDER)
            prev_end = end_time
            spread = _optional_float(row, "spread")
            bid_close = _optional_float(row, "bid_close")
            ask_close = _optional_float(row, "ask_close")
            if spread is None and bid_close is not None and ask_close is not None:
                spread = ask_close - bid_close
            if spread is not None and spread < 0:
                flags.append(QualityFlag.NEGATIVE_SPREAD)
            yield MarketBar(
                instrument=self.instrument,
                start_time=start_time,
                end_time=end_time,
                available_time=self._resolve_available_time(end_time, row),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=_optional_float(row, "volume"),
                bid_close=bid_close,
                ask_close=ask_close,
                spread=spread,
                source=f"csv:{self.path.name}",
                quality_flags=tuple(flags) if flags else (QualityFlag.OK,),
            )

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
