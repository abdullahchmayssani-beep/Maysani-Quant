"""Strategy contract.

A strategy returns a Signal: a direction and a score. It does not return a
position size, and it has no access to the risk engine, the broker, or cash.
Stop distance is *proposed* in price units; the risk engine decides whether it
is usable and what size it implies.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from maysani_quant.domain.enums import Action, ReasonCode
from maysani_quant.domain.models import FeatureSnapshot, PortfolioSnapshot, Signal, stable_hash


class Strategy(ABC):
    strategy_id: str = "abstract"
    version: str = "v0"

    def __init__(self, params: Mapping[str, Any] | None = None) -> None:
        self.params: dict[str, Any] = dict(params or {})
        self.params_hash = stable_hash(self.params)[:16]

    @abstractmethod
    def evaluate(
        self, features: FeatureSnapshot, portfolio: PortfolioSnapshot
    ) -> Signal:  # pragma: no cover - abstract
        ...

    def _signal(
        self,
        features: FeatureSnapshot,
        action: Action,
        score: float,
        reason_codes: tuple[ReasonCode, ...],
        stop_distance: float | None = None,
        horizon_bars: int = 1,
        expected_return: float | None = None,
        uncertainty: float | None = None,
    ) -> Signal:
        return Signal(
            as_of=features.as_of,
            instrument=features.instrument,
            strategy_id=self.strategy_id,
            strategy_version=self.version,
            action=action,
            score=score,
            horizon_bars=horizon_bars,
            snapshot_id=features.snapshot_id,
            expected_return=expected_return,
            uncertainty=uncertainty,
            stop_distance=stop_distance,
            reason_codes=reason_codes,
            params_hash=self.params_hash,
        )

    def describe(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "version": self.version,
            "params": dict(self.params),
            "params_hash": self.params_hash,
        }


_REGISTRY: dict[str, type[Strategy]] = {}


def register(cls: type[Strategy]) -> type[Strategy]:
    _REGISTRY[cls.strategy_id] = cls
    return cls


def build_strategy(strategy_id: str, params: Mapping[str, Any] | None = None) -> Strategy:
    if strategy_id not in _REGISTRY:
        known = ", ".join(sorted(_REGISTRY)) or "(none registered)"
        raise KeyError(f"unknown strategy '{strategy_id}'. Registered: {known}")
    return _REGISTRY[strategy_id](params)


def registered_strategies() -> list[str]:
    return sorted(_REGISTRY)
