"""Append-only journal (Sections 13.4, 21.7, 21.9).

Guarantees:
  * append-only - there is no update or delete method, by design
  * idempotent replay - a record whose content hash already exists is not
    written twice, so a restart cannot duplicate fills
  * deterministic ordering - sequence numbers are dense and monotonic

`written_at` is wall-clock and therefore excluded from the record hash;
including it would make two identical runs produce different journals and break
the determinism test for the wrong reason.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from maysani_quant.domain.models import to_jsonable
from maysani_quant.journal.schema import JournalEnvelope, make_record_id, utc_now


class Journal:
    def __init__(self, directory: str | Path, run_id: str, fsync: bool = False) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.path = self.directory / f"{run_id}.jsonl"
        self.fsync = fsync
        self._sequence = 0
        self._seen: set[str] = set()
        if self.path.exists():
            self._recover()

    def _recover(self) -> None:
        """Rebuild sequence and dedup index from an existing journal."""
        for envelope in self.read_all():
            self._sequence = max(self._sequence, envelope["sequence"])
            self._seen.add(envelope["record_id"])

    @property
    def sequence(self) -> int:
        return self._sequence

    def append(self, record_type: str, payload: Any) -> str:
        jsonable = to_jsonable(payload)
        record_id = make_record_id(self.run_id, record_type, self._sequence + 1, jsonable)
        if record_id in self._seen:
            return record_id  # idempotent: already durable
        self._sequence += 1
        envelope = JournalEnvelope(
            record_id=record_id,
            record_type=record_type,
            written_at=utc_now(),
            run_id=self.run_id,
            sequence=self._sequence,
            payload=jsonable if isinstance(jsonable, dict) else {"value": jsonable},
        )
        line = json.dumps(envelope.to_dict(), sort_keys=True, separators=(",", ":"))
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            if self.fsync:
                handle.flush()
                os.fsync(handle.fileno())
        self._seen.add(record_id)
        return record_id

    def read_all(self) -> Iterator[dict[str, Any]]:
        if not self.path.exists():
            return iter(())
        def _iter() -> Iterator[dict[str, Any]]:
            with self.path.open(encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
        return _iter()

    def read_type(self, record_type: str) -> list[dict[str, Any]]:
        return [r["payload"] for r in self.read_all() if r["record_type"] == record_type]

    def content_fingerprint(self) -> str:
        """Hash of the journal excluding wall-clock fields - for determinism tests."""
        from maysani_quant.domain.models import stable_hash

        stripped = [
            {k: v for k, v in r.items() if k != "written_at"} for r in self.read_all()
        ]
        return stable_hash(stripped)

    def save_checkpoint(self, state: dict[str, Any]) -> None:
        """Engine/risk/ledger state for restart. Overwrites: it is a pointer, not history."""
        checkpoint = self.directory / f"{self.run_id}.checkpoint.json"
        tmp = checkpoint.with_suffix(".tmp")
        tmp.write_text(json.dumps(to_jsonable(state), indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(checkpoint)

    def load_checkpoint(self) -> dict[str, Any] | None:
        checkpoint = self.directory / f"{self.run_id}.checkpoint.json"
        if not checkpoint.exists():
            return None
        return json.loads(checkpoint.read_text(encoding="utf-8"))


class InMemoryJournal(Journal):
    """Journal for tests. Same contract, no filesystem."""

    def __init__(self, run_id: str = "test") -> None:  # noqa: D107
        self.run_id = run_id
        self.records: list[dict[str, Any]] = []
        self._sequence = 0
        self._seen = set()
        self._checkpoint: dict[str, Any] | None = None

    def append(self, record_type: str, payload: Any) -> str:
        jsonable = to_jsonable(payload)
        record_id = make_record_id(self.run_id, record_type, self._sequence + 1, jsonable)
        if record_id in self._seen:
            return record_id
        self._sequence += 1
        self.records.append(
            {
                "record_id": record_id,
                "record_type": record_type,
                "written_at": datetime.min.isoformat(),
                "run_id": self.run_id,
                "sequence": self._sequence,
                "payload": jsonable if isinstance(jsonable, dict) else {"value": jsonable},
            }
        )
        self._seen.add(record_id)
        return record_id

    def read_all(self) -> Iterator[dict[str, Any]]:
        return iter(list(self.records))

    def save_checkpoint(self, state: dict[str, Any]) -> None:
        self._checkpoint = to_jsonable(state)

    def load_checkpoint(self) -> dict[str, Any] | None:
        return self._checkpoint
