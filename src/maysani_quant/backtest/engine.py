"""Event-driven backtest engine (Sections 13.1, 21.5).

Per-bar sequence, strictly ordered:

  bar t opens   -> any order intent created at t-1 fills at THIS open
                -> stop check against bar t's range (conservative resolution)
  bar t closes  -> financing accrues for day boundaries crossed
                -> mark portfolio at bar t close, write PortfolioSnapshot
                -> build PointInTimeView with available_time <= bar t close
                -> features -> strategy -> risk -> (maybe) order intent for t+1
                -> journal a DecisionRecord, WAIT included

The strategy therefore never sees bar t+1, and never fills at bar t's close.
The pending intent is the only state that crosses a bar boundary.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from maysani_quant.data.interfaces import PointInTimeView
from maysani_quant.data.validation import ValidationReport
from maysani_quant.domain.enums import Action, OrganismState, ReasonCode, Side
from maysani_quant.domain.models import (
    DecisionRecord,
    Fill,
    InstrumentSpec,
    MarketBar,
    OrderIntent,
    PortfolioSnapshot,
    TradeRecord,
    stable_hash,
)
from maysani_quant.execution.simulator import ExecutionSimulator
from maysani_quant.features.pipeline import FeaturePipeline
from maysani_quant.journal.store import Journal
from maysani_quant.portfolio.ledger import PortfolioLedger
from maysani_quant.risk.hard_limits import HardRiskEngine
from maysani_quant.risk.interfaces import MarketState
from maysani_quant.strategies.base import Strategy

ENGINE_VERSION = "engine-v0.1.0"


@dataclass
class BacktestResult:
    run_id: str
    experiment_id: str
    strategy_id: str
    strategy_version: str
    equity_curve: list[tuple[datetime, float]] = field(default_factory=list)
    snapshots: list[PortfolioSnapshot] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    fills: list[Fill] = field(default_factory=list)
    trades: list[TradeRecord] = field(default_factory=list)
    final_state: OrganismState = OrganismState.ALIVE
    bars_processed: int = 0
    warmup_bars: int = 0
    metrics: dict[str, Any] = field(default_factory=dict)
    data_hash: str = ""
    config_hash: str = ""
    dataset_is_synthetic: bool = False
    validation: ValidationReport | None = None
    journal_fingerprint: str = ""
    risk_veto_counts: dict[str, int] = field(default_factory=dict)


class BacktestEngine:
    def __init__(
        self,
        instrument: InstrumentSpec,
        pipeline: FeaturePipeline,
        strategy: Strategy,
        risk: HardRiskEngine,
        execution: ExecutionSimulator,
        ledger: PortfolioLedger,
        journal: Journal,
        bar_seconds: int,
        experiment_id: str,
        config_hash: str,
        data_hash: str,
        code_version: str = ENGINE_VERSION,
    ) -> None:
        self.instrument = instrument
        self.pipeline = pipeline
        self.strategy = strategy
        self.risk = risk
        self.execution = execution
        self.ledger = ledger
        self.journal = journal
        self.bar_seconds = bar_seconds
        self.experiment_id = experiment_id
        self.config_hash = config_hash
        self.data_hash = data_hash
        self.code_version = code_version

        self._pending: OrderIntent | None = None
        self._pending_stop_distance: float | None = None
        self._open_context: dict[str, Any] | None = None
        self._decision_seq = 0

    # ------------------------------------------------------------------- run
    def run(self, bars: Sequence[MarketBar], data_quality_ok: bool = True) -> BacktestResult:
        result = BacktestResult(
            run_id=self.journal.run_id,
            experiment_id=self.experiment_id,
            strategy_id=self.strategy.strategy_id,
            strategy_version=self.strategy.version,
            warmup_bars=self.pipeline.warmup_bars(),
            data_hash=self.data_hash,
            config_hash=self.config_hash,
        )
        self.journal.append(
            "RUN_HEADER",
            {
                "run_id": self.journal.run_id,
                "experiment_id": self.experiment_id,
                "strategy": self.strategy.describe(),
                "config_hash": self.config_hash,
                "data_hash": self.data_hash,
                "code_version": self.code_version,
                "risk_config_version": self.risk.config_version,
                "engine_version": ENGINE_VERSION,
            },
        )

        history: list[MarketBar] = []
        prev_bar: MarketBar | None = None

        for index, bar in enumerate(bars):
            # --- 1. fills at THIS bar's open, from the previous bar's decision
            if self._pending is not None:
                self._execute_pending(bar, result)

            # --- 2. stop check against this bar's range
            if self.ledger.position is not None:
                self._check_stop(bar, result)

            # --- 3. financing for day boundaries crossed while holding
            if self.ledger.position is not None and prev_bar is not None:
                days = self._day_boundaries(prev_bar.end_time, bar.end_time)
                if days:
                    amount = self.execution.costs.financing(
                        self.ledger.position.units,
                        self.ledger.position.side is Side.LONG,
                        days,
                    )
                    self.ledger.apply_financing(amount)

            # --- 4. mark at close
            history.append(bar)
            spread = self.execution.costs.spread_for(bar.spread)
            snapshot = self.ledger.mark(bar.end_time, bar.close, spread)
            result.snapshots.append(snapshot)
            result.equity_curve.append((bar.end_time, snapshot.equity))
            self.risk.observe_equity(snapshot.equity)

            day_key = bar.end_time.date().isoformat()
            if self.risk.state.session_date != day_key:
                self.risk.start_session(day_key, snapshot.equity)

            # --- 5. death is terminal: flatten once, then stop deciding
            if snapshot.state is OrganismState.DEAD:
                self._journal_decision(
                    bar, None, None, None, snapshot,
                    action=Action.WAIT,
                    signal_reasons=(ReasonCode.ORGANISM_DEAD,),
                    result=result,
                )
                result.bars_processed = index + 1
                break

            # --- 6. decide for t+1
            self._decide(bar, history, snapshot, spread, data_quality_ok, result)
            prev_bar = bar
            result.bars_processed = index + 1

        result.final_state = self.ledger.state
        result.risk_veto_counts = dict(self.risk.state.reject_counts)
        result.journal_fingerprint = self.journal.content_fingerprint()
        self.journal.save_checkpoint(
            {
                "ledger": self.ledger.to_state(),
                "risk": self.risk.state.to_dict(),
                "bars_processed": result.bars_processed,
                "last_timestamp": bars[result.bars_processed - 1].end_time.isoformat()
                if result.bars_processed
                else None,
            }
        )
        return result

    # ------------------------------------------------------------- internals
    def _day_boundaries(self, start: datetime, end: datetime) -> float:
        return float((end.date() - start.date()).days)

    def _execute_pending(self, bar: MarketBar, result: BacktestResult) -> None:
        intent = self._pending
        self._pending = None
        assert intent is not None
        fills = self.execution.submit(intent, bar)
        for fill in fills:
            if fill.size <= 0:
                continue
            realized = self.ledger.apply_fill(fill)
            result.fills.append(fill)
            self.journal.append("FILL", fill)
            if self.ledger.position is not None and self._pending_stop_distance:
                pos = self.ledger.position
                stop = (
                    pos.average_price - self._pending_stop_distance
                    if pos.side is Side.LONG
                    else pos.average_price + self._pending_stop_distance
                )
                self.ledger.set_stop(self.instrument.round_price(stop))
                self._open_context = {
                    "entry_time": fill.timestamp,
                    "entry_price": fill.price,
                    "units": fill.size,
                    "side": pos.side,
                    "decision_id": intent.decision_id,
                    "entry_costs": fill.total_cost,
                    "entry_index": len(result.snapshots),
                }
            elif self.ledger.position is None:
                self.risk.record_realized(realized)
                self._close_trade(fill, realized, result, exit_reason="SIGNAL")
        self._pending_stop_distance = None

    def _check_stop(self, bar: MarketBar, result: BacktestResult) -> None:
        position = self.ledger.position
        assert position is not None
        hit, price, note = self.execution.resolve_stop(position, bar)
        if not hit or price is None:
            return
        fill = self.execution.stop_fill(position, bar, price, note)
        realized = self.ledger.apply_fill(fill)
        result.fills.append(fill)
        self.journal.append("FILL", fill)
        self.risk.record_realized(realized)
        self._close_trade(fill, realized, result, exit_reason=f"STOP:{note}")
        # A stop invalidates any order queued for the next open.
        self._pending = None
        self._pending_stop_distance = None

    def _close_trade(
        self, fill: Fill, realized: float, result: BacktestResult, exit_reason: str
    ) -> None:
        ctx = self._open_context
        if ctx is None:
            return
        entry_costs = float(ctx.get("entry_costs", 0.0))
        total_costs = entry_costs + fill.total_cost
        trade = TradeRecord(
            trade_id=stable_hash({"entry": ctx["entry_time"].isoformat(), "exit": fill.timestamp.isoformat()})[:24],
            instrument=fill.instrument,
            side=ctx["side"],
            units=ctx["units"],
            entry_time=ctx["entry_time"],
            entry_price=ctx["entry_price"],
            exit_time=fill.timestamp,
            exit_price=fill.price,
            gross_pnl=realized + fill.commission,
            costs=total_costs,
            net_pnl=realized - fill.commission,
            financing=0.0,
            duration_bars=max(0, len(result.snapshots) - int(ctx.get("entry_index", 0))),
            entry_decision_id=str(ctx.get("decision_id", "")),
            exit_decision_id=fill.intent_id,
            strategy_id=self.strategy.strategy_id,
            exit_reason=exit_reason,
        )
        result.trades.append(trade)
        self.journal.append("TRADE", trade)
        self._open_context = None

    def _decide(
        self,
        bar: MarketBar,
        history: list[MarketBar],
        snapshot: PortfolioSnapshot,
        spread: float,
        data_quality_ok: bool,
        result: BacktestResult,
    ) -> None:
        as_of = bar.end_time
        view = PointInTimeView(history, as_of, self.instrument.symbol)
        features = self.pipeline.compute(view, as_of)
        if features is None:
            self._journal_decision(
                bar, None, None, None, snapshot,
                action=Action.WAIT,
                signal_reasons=(ReasonCode.WARMUP,),
                result=result,
            )
            return

        signal = self.strategy.evaluate(features, snapshot)
        market = MarketState(
            as_of=as_of,
            instrument=self.instrument.symbol,
            reference_price=bar.close,
            spread=spread,
            atr=features.get("atr"),
            realized_vol=features.get("realized_vol"),
            staleness_bars=(as_of - bar.available_time).total_seconds() / self.bar_seconds
            if self.bar_seconds
            else 0.0,
            data_quality_ok=data_quality_ok,
        )
        risk_decision = self.risk.assess(signal, snapshot, market, self.instrument)

        if signal.action is not Action.WAIT and risk_decision.permits_order:
            is_reducing = snapshot.position is not None and (
                (snapshot.position.side is Side.LONG and signal.action is Action.SELL)
                or (snapshot.position.side is Side.SHORT and signal.action is Action.BUY)
            )
            decision_id = self._next_decision_id(bar)
            intent = self.execution.build_intent(
                risk_decision,
                signal.action,
                self.instrument.symbol,
                as_of,
                decision_id,
                is_reducing=is_reducing,
            )
            self._pending = intent
            self._pending_stop_distance = None if is_reducing else signal.stop_distance
            self.journal.append("ORDER_INTENT", intent)

        self._journal_decision(
            bar, features, signal, risk_decision, snapshot,
            action=signal.action,
            signal_reasons=signal.reason_codes,
            result=result,
        )

    def _next_decision_id(self, bar: MarketBar) -> str:
        self._decision_seq += 1
        return stable_hash(
            {"run": self.journal.run_id, "seq": self._decision_seq, "t": bar.end_time.isoformat()}
        )[:32]

    def _journal_decision(
        self,
        bar: MarketBar,
        features: Any,
        signal: Any,
        risk_decision: Any,
        snapshot: PortfolioSnapshot,
        action: Action,
        signal_reasons: tuple[ReasonCode, ...],
        result: BacktestResult,
    ) -> None:
        """Every bar produces exactly one DecisionRecord - WAIT included (21.9)."""
        expected_costs = 0.0
        if risk_decision is not None and risk_decision.approved_size > 0:
            spread = self.execution.costs.spread_for(bar.spread)
            expected_costs = (
                spread / 2.0 + self.execution.costs.config.slippage_price
            ) * risk_decision.approved_size + self.execution.costs.commission(
                risk_decision.approved_size
            )
        record = DecisionRecord(
            decision_id=self._next_decision_id(bar),
            as_of=bar.end_time,
            instrument=self.instrument.symbol,
            action=action,
            strategy_id=self.strategy.strategy_id,
            strategy_version=self.strategy.version,
            snapshot_id=features.snapshot_id if features is not None else "",
            signal_score=signal.score if signal is not None else 0.0,
            expected_costs=expected_costs,
            risk_verdict=risk_decision.verdict if risk_decision is not None else None,
            risk_decision_id=risk_decision.decision_id if risk_decision is not None else None,
            risk_reason_codes=risk_decision.reason_codes if risk_decision is not None else (),
            approved_size=risk_decision.approved_size if risk_decision is not None else 0.0,
            portfolio_equity=snapshot.equity,
            portfolio_state=snapshot.state,
            experiment_id=self.experiment_id,
            code_version=self.code_version,
            config_hash=self.config_hash,
            data_hash=self.data_hash,
            signal_reason_codes=signal_reasons,
        )
        result.decisions.append(record)
        self.journal.append("DECISION", record)
        self.journal.append("PORTFOLIO", snapshot)
