"""Execution-side value objects.

OrderIntent / Fill / FillStatus live in `domain` because the risk and portfolio
layers speak the same vocabulary. This module re-exports them so execution code
reads naturally, and documents the states V0.1 models but does not yet produce.

Modelled and produced in V0.1: FILLED, REJECTED.
Modelled, not yet produced:     PARTIAL, CANCELLED, UNKNOWN.

UNKNOWN matters for a later live adapter: an API timeout is not a rejection,
and the domain must be able to say "we do not know" without lying either way
(Section 13.2).
"""
from __future__ import annotations

from maysani_quant.domain.enums import Action, FillStatus, OrderType
from maysani_quant.domain.models import Fill, OrderIntent

PRODUCED_IN_V0_1 = (FillStatus.FILLED, FillStatus.REJECTED)
MODELLED_NOT_PRODUCED = (FillStatus.PARTIAL, FillStatus.CANCELLED, FillStatus.UNKNOWN)

__all__ = [
    "Action", "FillStatus", "OrderType", "Fill", "OrderIntent",
    "PRODUCED_IN_V0_1", "MODELLED_NOT_PRODUCED",
]
