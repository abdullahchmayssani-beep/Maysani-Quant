"""Journal record envelope.

One append-only JSONL file per run per record type. Chosen over SQLite for V0.1
because a text file is trivially diffable and cannot silently migrate. The
`Journal` interface is narrow enough that a PostgreSQL store can replace it
without touching the engine (Section 21.7).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from maysani_quant.domain.models import stable_hash, to_jsonable

JOURNAL_SCHEMA_VERSION = "journal-v0.1.0"


@dataclass(frozen=True)
class JournalEnvelope:
    record_id: str
    record_type: str
    written_at: datetime
    run_id: str
    sequence: int
    payload: dict[str, Any]
    schema_version: str = JOURNAL_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "record_type": self.record_type,
            "written_at": self.written_at.isoformat(),
            "run_id": self.run_id,
            "sequence": self.sequence,
            "schema_version": self.schema_version,
            "payload": to_jsonable(self.payload),
        }


def make_record_id(run_id: str, record_type: str, sequence: int, payload: Any) -> str:
    """Content-addressed record id.

    `sequence` is deliberately NOT part of the hash. A replay of the same run
    starts numbering after the recovered records, so including the sequence
    would give identical events new ids and duplicate every fill on restart.
    Record identity is (run, type, content) - and since every payload carries
    its own timestamp, two genuinely distinct events cannot collide.
    """
    return stable_hash(
        {"run": run_id, "type": record_type, "payload": to_jsonable(payload)}
    )[:32]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
