"""Run assembly.

The only place where data source, features, strategy, risk, execution, ledger
and journal are wired together. Keeping the wiring in one function means the
authority chain can be read top to bottom in about forty lines.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from maysani_quant.backtest.engine import ENGINE_VERSION, BacktestEngine, BacktestResult
from maysani_quant.backtest.metrics import MetricsBundle, compute_metrics
from maysani_quant.config import AppConfig, StrategySpec
from maysani_quant.data.csv_source import CsvMarketDataSource
from maysani_quant.data.service import MarketDataService
from maysani_quant.execution.costs import CostModel
from maysani_quant.execution.simulator import ExecutionSimulator
from maysani_quant.experiments.registry import ExperimentRegistry, code_version
from maysani_quant.features.pipeline import FeaturePipeline
from maysani_quant.journal.store import Journal
from maysani_quant.portfolio.ledger import PortfolioLedger
from maysani_quant.risk.hard_limits import HardRiskEngine
from maysani_quant.risk.interfaces import RiskState


@dataclass
class RunOutput:
    result: BacktestResult
    metrics: MetricsBundle
    experiment_id: str


def run_strategy(
    config: AppConfig,
    spec: StrategySpec,
    source: CsvMarketDataSource | MarketDataService,
    registry: ExperimentRegistry,
    run_suffix: str = "",
) -> RunOutput:
    from maysani_quant.strategies.base import build_strategy

    strategy = build_strategy(spec.id, spec.params)
    bars = list(source.all_bars())

    experiment = registry.open_experiment(
        hypothesis=spec.hypothesis or config.hypothesis or "unstated",
        strategy_id=strategy.strategy_id,
        strategy_version=strategy.version,
        params=strategy.params,
        config_hash=config.config_hash,
        data_hash=source.data_hash,
        dataset_path=source.dataset_path,
        cost_model_hash=config.costs.hash,
        risk_config_version=config.risk.config_version,
        window_start=bars[0].end_time if bars else None,
        window_end=bars[-1].end_time if bars else None,
    )

    run_id = f"{config.experiment_name}_{spec.id}{run_suffix}_{experiment.experiment_id[:8]}"
    journal = Journal(config.journal_dir, run_id)

    cost_model = CostModel(config.costs)
    engine = BacktestEngine(
        instrument=config.instrument,
        pipeline=FeaturePipeline(config.features),
        strategy=strategy,
        risk=HardRiskEngine(config.risk, RiskState(peak_equity=config.initial_equity)),
        execution=ExecutionSimulator(
            cost_model, config.instrument, config.ambiguous_bar_policy
        ),
        ledger=PortfolioLedger(
            initial_equity=config.initial_equity,
            instrument=config.instrument,
            death_threshold=config.death_threshold,
            margin_requirement_pct=config.risk.margin_requirement_pct,
        ),
        journal=journal,
        bar_seconds=config.bar_seconds,
        experiment_id=experiment.experiment_id,
        config_hash=config.config_hash,
        data_hash=source.data_hash,
        code_version=code_version(),
    )

    try:
        result = engine.run(bars, data_quality_ok=source.validation.ok)
    except Exception as exc:  # failures stay in the registry (Section 13.4)
        registry.close_experiment(experiment, "FAILED", notes=f"{type(exc).__name__}: {exc}")
        raise

    result.dataset_is_synthetic = source.is_synthetic
    result.validation = source.validation

    spread_slippage = sum(f.spread_cost + f.slippage_cost for f in result.fills)
    commissions = sum(f.commission for f in result.fills)
    financing = engine.ledger.financing_paid_cum
    metrics = compute_metrics(
        snapshots=result.snapshots,
        trades=result.trades,
        initial_equity=config.initial_equity,
        timeframe=config.timeframe,
        total_costs=spread_slippage + commissions + financing,
        spread_slippage_costs=spread_slippage,
        financing_costs=financing,
        commissions=commissions,
    )
    metrics.values["risk_vetoes"] = dict(result.risk_veto_counts)
    metrics.values["entry_vetoes_total"] = sum(result.risk_veto_counts.values())
    result.metrics = metrics.to_dict()
    registry.close_experiment(experiment, "COMPLETED", metrics=metrics.values)
    return RunOutput(result=result, metrics=metrics, experiment_id=experiment.experiment_id)


def build_source(
    config: AppConfig, dataset_override: str | None = None
) -> CsvMarketDataSource | MarketDataService:
    """The one place a provider is chosen (ADR 0003). Everything downstream
    of this function only ever sees a `MarketDataSource`-shaped object."""
    if config.data_provider == "csv":
        path = dataset_override or config.dataset_path
        return CsvMarketDataSource(
            path=path,
            instrument=config.instrument.symbol,
            timeframe=config.timeframe,
            timestamp_column=config.timestamp_column,
            available_time_policy=config.available_time_policy,
            available_time_lag_seconds=config.available_time_lag_seconds,
            price_kind=config.price_kind,
            bar_duration_seconds=config.bar_seconds,
        )
    if config.data_provider == "dukascopy":
        from maysani_quant.data.providers.dukascopy import DukascopyProvider

        assert config.dukascopy is not None  # enforced by config.py's load_config
        provider = DukascopyProvider(price_precision=config.instrument.price_precision)
        return MarketDataService(
            provider,
            instrument=config.instrument.symbol,
            start=config.dukascopy.start,
            end=config.dukascopy.end,
            bar_seconds=config.bar_seconds,
            timeframe=config.timeframe,
            available_time_policy=config.available_time_policy,
            available_time_lag_seconds=config.available_time_lag_seconds,
            raw_root=config.dukascopy.raw_root,
            canonical_root=config.dukascopy.canonical_root,
            require_bid_ask=config.dukascopy.require_bid_ask,
        )
    raise ValueError(f"unknown data.provider: {config.data_provider}")  # pragma: no cover


def engine_version() -> str:
    return ENGINE_VERSION


def ensure_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
