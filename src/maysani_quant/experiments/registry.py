"""Experiment registry (Section 13.4).

Every trial gets an immutable record before it runs, and the record is closed
with a status afterwards - including FAILED and ABANDONED. There is no delete
method. A registry you can prune is a registry that produces a factor zoo, and
the count of trials is itself a statistic the deflated Sharpe calculation needs.
"""
from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from maysani_quant.domain.models import ExperimentRecord, stable_hash, to_jsonable

VALID_STATUSES = frozenset({"RUNNING", "COMPLETED", "FAILED", "ABANDONED"})


def code_version() -> str:
    """Git commit if available, else an explicit marker. Never a guess."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            dirty = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            suffix = "-dirty" if dirty.stdout.strip() else ""
            return out.stdout.strip() + suffix
    except (OSError, subprocess.SubprocessError):
        pass
    return "UNVERSIONED"


class ExperimentRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _append_line(self, payload: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")

    def open_experiment(
        self,
        hypothesis: str,
        strategy_id: str,
        strategy_version: str,
        params: Mapping[str, Any],
        config_hash: str,
        data_hash: str,
        dataset_path: str,
        cost_model_hash: str,
        risk_config_version: str,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        parent_experiment_id: str | None = None,
        notes: str = "",
    ) -> ExperimentRecord:
        created = datetime.now(UTC)
        experiment_id = stable_hash(
            {
                "strategy": f"{strategy_id}@{strategy_version}",
                "params": to_jsonable(params),
                "config_hash": config_hash,
                "data_hash": data_hash,
                "cost_model_hash": cost_model_hash,
                "risk_config_version": risk_config_version,
                "window": [
                    window_start.isoformat() if window_start else None,
                    window_end.isoformat() if window_end else None,
                ],
            }
        )[:24]
        record = ExperimentRecord(
            experiment_id=experiment_id,
            created_at=created,
            hypothesis=hypothesis,
            strategy_id=strategy_id,
            strategy_version=strategy_version,
            params=dict(params),
            config_hash=config_hash,
            data_hash=data_hash,
            dataset_path=dataset_path,
            code_version=code_version(),
            window_start=window_start,
            window_end=window_end,
            cost_model_hash=cost_model_hash,
            risk_config_version=risk_config_version,
            status="RUNNING",
            parent_experiment_id=parent_experiment_id,
            notes=notes,
        )
        self._append_line({"event": "OPEN", **to_jsonable(record)})
        return record

    def close_experiment(
        self, record: ExperimentRecord, status: str, metrics: Mapping[str, Any] | None = None,
        notes: str = "",
    ) -> None:
        if status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        self._append_line(
            {
                "event": "CLOSE",
                "experiment_id": record.experiment_id,
                "closed_at": datetime.now(UTC).isoformat(),
                "status": status,
                "metrics": to_jsonable(dict(metrics or {})),
                "notes": notes,
            }
        )

    def trial_count(self) -> int:
        """Total opened trials - the multiple-testing denominator (Section 13.4)."""
        return sum(1 for row in self._load() if row.get("event") == "OPEN")

    def find(self, experiment_id: str) -> dict[str, Any] | None:
        opened = None
        closed = None
        for row in self._load():
            if row.get("experiment_id") != experiment_id:
                continue
            if row.get("event") == "OPEN":
                opened = row
            elif row.get("event") == "CLOSE":
                closed = row
        if opened is None:
            return None
        return {"open": opened, "close": closed}

    def all_experiments(self) -> list[dict[str, Any]]:
        return self._load()
