"""Experiment schema notes.

The ExperimentRecord dataclass lives in `domain.models` because it is part of
the domain vocabulary, not a registry implementation detail. This module holds
the surrounding contract so a future PostgreSQL registry has one place to read.

Required fields for any trial (Section 13.4):
  hypothesis, feature set, parameters, data snapshot, train/validation/test
  windows, cost model, code commit, result, status.

Status lifecycle:
  RUNNING -> COMPLETED | FAILED | ABANDONED     (terminal, never re-opened)

Retention: permanent. FAILED and ABANDONED trials are part of the multiple
testing denominator and are never pruned.
"""
from __future__ import annotations

from maysani_quant.domain.models import ExperimentRecord

REQUIRED_FIELDS = (
    "experiment_id", "hypothesis", "strategy_id", "strategy_version", "params",
    "config_hash", "data_hash", "code_version", "cost_model_hash",
    "risk_config_version", "status",
)

TERMINAL_STATUSES = ("COMPLETED", "FAILED", "ABANDONED")

__all__ = ["ExperimentRecord", "REQUIRED_FIELDS", "TERMINAL_STATUSES"]
