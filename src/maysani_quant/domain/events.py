"""Explicit, ordered simulation events (Section 13.1).

The engine never "looks at a dataframe". It consumes an ordered event stream so
that the same loop can later be fed by a paper/shadow/live adapter without the
decision code learning anything new about time.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Any

from maysani_quant.domain.models import MarketBar


class EventKind(IntEnum):
    """Order matters: within one timestamp, events resolve in this sequence."""

    BAR_OPEN = 10
    FILL = 20
    BAR_CLOSE = 30
    FINANCING = 40
    MARK = 50
    DECISION = 60


@dataclass(frozen=True)
class Event:
    kind: EventKind
    timestamp: datetime
    bar: MarketBar | None = None
    payload: Any = None

    def sort_key(self) -> tuple[datetime, int]:
        return (self.timestamp, int(self.kind))
