"""Cost model (Section 13.2).

No "realistic" constant is fabricated anywhere in this file. Every number comes
from config, and `CostModel.describe()` is printed in the report so a reader
knows what was assumed rather than guessing.

Spread convention: `reference_price` is a midpoint. A buy executes at
mid + spread/2 + slippage; a sell at mid - spread/2 - slippage. If the dataset
carries true bid/ask, those are used instead and the scenario spread is ignored.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from maysani_quant.domain.enums import Action
from maysani_quant.domain.models import stable_hash


@dataclass(frozen=True)
class CostConfig:
    spread_model: str = "fixed"          # fixed | dataset
    fixed_spread_price: float = 0.00012
    slippage_price: float = 0.0
    commission_per_unit: float = 0.0
    commission_minimum: float = 0.0
    financing_per_unit_per_day_long: float = 0.0
    financing_per_unit_per_day_short: float = 0.0
    scenario_name: str = "baseline"

    def describe(self) -> dict[str, Any]:
        return {
            "scenario": self.scenario_name,
            "spread_model": self.spread_model,
            "fixed_spread_price": self.fixed_spread_price,
            "slippage_price": self.slippage_price,
            "commission_per_unit": self.commission_per_unit,
            "commission_minimum": self.commission_minimum,
            "financing_long_per_unit_per_day": self.financing_per_unit_per_day_long,
            "financing_short_per_unit_per_day": self.financing_per_unit_per_day_short,
        }

    @property
    def hash(self) -> str:
        return stable_hash(self.describe())[:16]


@dataclass(frozen=True)
class ExecutionPrice:
    price: float
    reference_price: float
    spread_used: float
    spread_cost: float
    slippage_cost: float
    commission: float

    @property
    def total_cost(self) -> float:
        return self.spread_cost + self.slippage_cost + self.commission


class CostModel:
    def __init__(self, config: CostConfig) -> None:
        self.config = config

    def describe(self) -> dict[str, Any]:
        return self.config.describe()

    def spread_for(self, bar_spread: float | None) -> float:
        """Dataset spread wins when available; otherwise the configured scenario."""
        if self.config.spread_model == "dataset":
            if bar_spread is None:
                raise ValueError(
                    "spread_model='dataset' but the bar carries no spread. "
                    "Supply bid/ask data or switch to a documented fixed scenario."
                )
            return bar_spread
        return self.config.fixed_spread_price

    def commission(self, size: float) -> float:
        fee = abs(size) * self.config.commission_per_unit
        return max(fee, self.config.commission_minimum) if size else 0.0

    def execution_price(
        self, action: Action, reference_price: float, size: float, bar_spread: float | None
    ) -> ExecutionPrice:
        """Signed price adjustment. Costs are always charged against us."""
        if action is Action.WAIT:
            raise ValueError("WAIT has no execution price")
        spread = self.spread_for(bar_spread)
        half = spread / 2.0
        slip = self.config.slippage_price
        direction = 1.0 if action is Action.BUY else -1.0
        price = reference_price + direction * (half + slip)
        units = abs(size)
        return ExecutionPrice(
            price=price,
            reference_price=reference_price,
            spread_used=spread,
            spread_cost=half * units,
            slippage_cost=slip * units,
            commission=self.commission(units),
        )

    def financing(self, units: float, is_long: bool, days: float) -> float:
        """Cost (positive) or credit (negative) for holding across day boundaries.

        V0.1 default is zero with the hook present. A broker rollover model is
        deferred until the point-in-time rate layer exists (Section 21.6).
        """
        rate = (
            self.config.financing_per_unit_per_day_long
            if is_long
            else self.config.financing_per_unit_per_day_short
        )
        return abs(units) * rate * days
