"""Configuration loading (Section 21.8).

Every tunable lives here and is hashed into the experiment record. If a number
influences a result and is not in this file's output, that is a bug.

Loading is strict: unknown top-level keys raise rather than being ignored, so a
typo in a risk limit fails loudly instead of silently running the default.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from maysani_quant.domain.enums import AmbiguousBarPolicy
from maysani_quant.domain.models import InstrumentSpec, stable_hash
from maysani_quant.execution.costs import CostConfig
from maysani_quant.features.pipeline import FeatureConfig
from maysani_quant.risk.interfaces import RiskConfig

BAR_SECONDS = {"M1": 60, "M5": 300, "M15": 900, "H1": 3600, "H4": 14400, "D1": 86400}

TOP_LEVEL_KEYS = {
    "version", "experiment", "instrument", "account", "data", "costs",
    "execution", "risk", "features", "strategies", "journal", "report",
}


@dataclass
class StrategySpec:
    id: str
    params: dict[str, Any] = field(default_factory=dict)
    hypothesis: str = ""


@dataclass
class AppConfig:
    version: str
    experiment_name: str
    hypothesis: str
    instrument: InstrumentSpec
    initial_equity: float
    death_threshold: float
    dataset_path: str
    timeframe: str
    timestamp_column: str
    available_time_policy: str
    available_time_lag_seconds: int
    price_kind: str
    costs: CostConfig
    risk: RiskConfig
    features: FeatureConfig
    strategies: list[StrategySpec]
    ambiguous_bar_policy: AmbiguousBarPolicy
    journal_dir: str
    report_dir: str
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def bar_seconds(self) -> int:
        return BAR_SECONDS.get(self.timeframe, 86400)

    @property
    def config_hash(self) -> str:
        """Hash of the FULL raw config. Report paths included on purpose:
        two runs that wrote different files are not the same run."""
        return stable_hash(self.raw)

    def summary(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "experiment": self.experiment_name,
            "instrument": self.instrument.symbol,
            "timeframe": self.timeframe,
            "initial_equity": self.initial_equity,
            "death_threshold": self.death_threshold,
            "risk_config_version": self.risk.config_version,
            "cost_scenario": self.costs.scenario_name,
            "config_hash": self.config_hash[:16],
        }


def _require(mapping: Mapping[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise KeyError(f"config is missing required key '{key}' under {where}")
    return mapping[key]


def load_config(path: str | Path) -> AppConfig:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"config at {path} did not parse to a mapping")

    unknown = set(raw) - TOP_LEVEL_KEYS
    if unknown:
        raise ValueError(
            f"unknown config keys {sorted(unknown)}. Refusing to run with an "
            "unrecognised setting - a typo here is a silent risk change."
        )

    instrument_raw = _require(raw, "instrument", "root")
    account = _require(raw, "account", "root")
    data = _require(raw, "data", "root")
    costs_raw = raw.get("costs", {})
    risk_raw = raw.get("risk", {})
    features_raw = raw.get("features", {})
    execution_raw = raw.get("execution", {})
    experiment_raw = raw.get("experiment", {})
    journal_raw = raw.get("journal", {})
    report_raw = raw.get("report", {})

    instrument = InstrumentSpec(
        symbol=_require(instrument_raw, "symbol", "instrument"),
        base_currency=_require(instrument_raw, "base_currency", "instrument"),
        quote_currency=_require(instrument_raw, "quote_currency", "instrument"),
        price_precision=int(instrument_raw.get("price_precision", 5)),
        size_step=float(instrument_raw.get("size_step", 1.0)),
        min_order_size=float(instrument_raw.get("min_order_size", 1.0)),
        contract_multiplier=float(instrument_raw.get("contract_multiplier", 1.0)),
    )

    strategies = [
        StrategySpec(
            id=_require(item, "id", "strategies[]"),
            params=dict(item.get("params", {})),
            hypothesis=item.get("hypothesis", ""),
        )
        for item in raw.get("strategies", [])
    ]
    if not strategies:
        raise ValueError("config lists no strategies; V0.1 requires baselines to be explicit")

    return AppConfig(
        version=str(raw.get("version", "unversioned")),
        experiment_name=experiment_raw.get("name", "unnamed"),
        hypothesis=experiment_raw.get("hypothesis", ""),
        instrument=instrument,
        initial_equity=float(_require(account, "initial_equity", "account")),
        death_threshold=float(_require(account, "death_threshold", "account")),
        dataset_path=str(_require(data, "path", "data")),
        timeframe=str(_require(data, "timeframe", "data")),
        timestamp_column=str(data.get("timestamp_column", "timestamp")),
        available_time_policy=str(data.get("available_time_policy", "bar_close")),
        available_time_lag_seconds=int(data.get("available_time_lag_seconds", 0)),
        price_kind=str(data.get("price_kind", "midpoint")),
        costs=CostConfig(
            spread_model=str(costs_raw.get("spread_model", "fixed")),
            fixed_spread_price=float(costs_raw.get("fixed_spread_price", 0.00012)),
            slippage_price=float(costs_raw.get("slippage_price", 0.0)),
            commission_per_unit=float(costs_raw.get("commission_per_unit", 0.0)),
            commission_minimum=float(costs_raw.get("commission_minimum", 0.0)),
            financing_per_unit_per_day_long=float(
                costs_raw.get("financing_per_unit_per_day_long", 0.0)
            ),
            financing_per_unit_per_day_short=float(
                costs_raw.get("financing_per_unit_per_day_short", 0.0)
            ),
            scenario_name=str(costs_raw.get("scenario_name", "baseline")),
        ),
        risk=RiskConfig(
            config_version=str(risk_raw.get("config_version", "risk-v0.1.0")),
            risk_per_trade_pct=float(risk_raw.get("risk_per_trade_pct", 0.01)),
            max_leverage=float(risk_raw.get("max_leverage", 5.0)),
            margin_requirement_pct=float(risk_raw.get("margin_requirement_pct", 0.20)),
            max_margin_utilisation=float(risk_raw.get("max_margin_utilisation", 0.50)),
            max_open_risk_pct=float(risk_raw.get("max_open_risk_pct", 0.02)),
            daily_loss_limit_pct=float(risk_raw.get("daily_loss_limit_pct", 0.03)),
            max_drawdown_pct=float(risk_raw.get("max_drawdown_pct", 0.20)),
            drawdown_throttle=tuple(
                (float(a), float(b)) for a, b in risk_raw.get(
                    "drawdown_throttle", [[0.05, 1.0], [0.10, 0.5], [0.15, 0.25]]
                )
            ),
            max_spread_price=float(risk_raw.get("max_spread_price", 0.0005)),
            max_realized_vol=float(risk_raw.get("max_realized_vol", 0.05)),
            vol_target=(
                float(risk_raw["vol_target"]) if risk_raw.get("vol_target") is not None else None
            ),
            max_staleness_bars=float(risk_raw.get("max_staleness_bars", 2.0)),
            min_stop_distance_price=float(risk_raw.get("min_stop_distance_price", 0.0001)),
            max_stop_distance_price=float(risk_raw.get("max_stop_distance_price", 0.05)),
            event_window_blocks_entry=bool(risk_raw.get("event_window_blocks_entry", True)),
        ),
        features=FeatureConfig(
            momentum_lookback=int(features_raw.get("momentum_lookback", 20)),
            ma_fast=int(features_raw.get("ma_fast", 10)),
            ma_slow=int(features_raw.get("ma_slow", 50)),
            vol_lookback=int(features_raw.get("vol_lookback", 20)),
            zscore_lookback=int(features_raw.get("zscore_lookback", 20)),
            atr_lookback=int(features_raw.get("atr_lookback", 14)),
        ),
        strategies=strategies,
        ambiguous_bar_policy=AmbiguousBarPolicy(
            execution_raw.get("ambiguous_bar_policy", "adverse")
        ),
        journal_dir=str(journal_raw.get("path", "runs")),
        report_dir=str(report_raw.get("output_dir", "runs")),
        raw=raw,
    )
