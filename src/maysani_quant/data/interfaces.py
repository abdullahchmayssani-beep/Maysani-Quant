"""Data access contracts.

The look-ahead ban (Section 13.3) is enforced here rather than trusted to
strategy authors. `PointInTimeView` is the ONLY object handed to feature and
strategy code, and it raises rather than silently returning future rows.
"""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator, Protocol, Sequence

from maysani_quant.domain.models import MarketBar


class LookAheadError(RuntimeError):
    """Raised when code asks for information it could not have had at as_of.

    This is a hard failure on purpose. A silently-empty result would let a
    leaking backtest run to completion and look merely unprofitable.
    """


class MarketDataSource(Protocol):
    instrument: str
    dataset_path: str
    data_hash: str

    def iter_events(
        self, start: datetime | None = None, end: datetime | None = None
    ) -> Iterator[MarketBar]:  # pragma: no cover - protocol
        ...

    def all_bars(self) -> Sequence[MarketBar]:  # pragma: no cover - protocol
        ...


class PointInTimeView:
    """A read-only window over history that ends at `as_of`.

    Filtering, not raising, is the constructor's job: a publication lag is a
    normal fact about data, and a bar that is not yet available is simply not in
    the view. `excluded_count` records how many were held back so the engine can
    log it rather than discover it later.

    Raising is reserved for *queries* that reach past `as_of` - that is code
    asking for the future, which is a bug rather than a data property. Pass
    `strict=True` where the caller believes it has already filtered and wants
    that belief checked.
    """

    __slots__ = ("_bars", "_as_of", "_instrument", "_excluded")

    def __init__(
        self,
        bars: Sequence[MarketBar],
        as_of: datetime,
        instrument: str,
        strict: bool = False,
    ) -> None:
        eligible = [b for b in bars if b.available_time <= as_of]
        excluded = len(bars) - len(eligible)
        if strict and excluded:
            raise LookAheadError(
                f"{excluded} bar(s) with available_time > as_of={as_of.isoformat()} "
                "were passed to a strict PointInTimeView"
            )
        self._bars: tuple[MarketBar, ...] = tuple(eligible)
        self._as_of = as_of
        self._instrument = instrument
        self._excluded = excluded

    @property
    def excluded_count(self) -> int:
        """Bars withheld because they were not yet available at as_of."""
        return self._excluded

    @property
    def as_of(self) -> datetime:
        return self._as_of

    @property
    def instrument(self) -> str:
        return self._instrument

    def __len__(self) -> int:
        return len(self._bars)

    def __iter__(self) -> Iterator[MarketBar]:
        return iter(self._bars)

    @property
    def bars(self) -> tuple[MarketBar, ...]:
        return self._bars

    def last(self, n: int = 1) -> tuple[MarketBar, ...]:
        if n <= 0:
            raise ValueError("n must be positive")
        return self._bars[-n:]

    def latest(self) -> MarketBar | None:
        return self._bars[-1] if self._bars else None

    def closes(self, n: int | None = None) -> list[float]:
        bars = self._bars if n is None else self._bars[-n:]
        return [b.close for b in bars]

    def at_or_after(self, when: datetime) -> Iterable[MarketBar]:
        if when > self._as_of:
            raise LookAheadError(
                f"requested bars at {when.isoformat()} from a view as_of {self._as_of.isoformat()}"
            )
        return (b for b in self._bars if b.available_time >= when)

    def require(self, n: int) -> tuple[MarketBar, ...]:
        """Return the last n bars, or raise if warm-up is incomplete."""
        if len(self._bars) < n:
            raise InsufficientHistory(
                f"need {n} bars, view holds {len(self._bars)} at {self._as_of.isoformat()}"
            )
        return self._bars[-n:]


class InsufficientHistory(RuntimeError):
    """Warm-up not complete. Callers should emit WAIT with reason WARMUP."""
