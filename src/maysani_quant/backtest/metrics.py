"""Performance metrics (Section 13.6).

Two deliberate choices:

1. Sharpe is returned WITH its frequency and a lag-1 autocorrelation estimate
   attached, because an annualised Sharpe with no disclosure of either is close
   to meaningless on a short sample.
2. Nothing here is labelled "good". The report prints measured values and the
   assumptions behind them; judgement is a separate, human step.

Deflated Sharpe / PBO are deferred until an experiment sweep exists to deflate
against - the trial count lives in the experiment registry, not in a single run.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Sequence

from maysani_quant.domain.models import PortfolioSnapshot, TradeRecord

PERIODS_PER_YEAR = {"D1": 252, "H1": 252 * 24, "H4": 252 * 6, "M15": 252 * 96}


@dataclass
class MetricsBundle:
    values: dict[str, Any] = field(default_factory=dict)
    disclosures: dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return self.values[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {"metrics": dict(self.values), "disclosures": dict(self.disclosures)}


def _returns(equity: Sequence[float]) -> list[float]:
    out = []
    for i in range(1, len(equity)):
        prev = equity[i - 1]
        if prev <= 0:
            out.append(0.0)
        else:
            out.append(equity[i] / prev - 1.0)
    return out


def _stdev(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(var)


def autocorrelation_lag1(values: Sequence[float]) -> float:
    if len(values) < 3:
        return 0.0
    mean = sum(values) / len(values)
    num = sum((values[i] - mean) * (values[i - 1] - mean) for i in range(1, len(values)))
    den = sum((v - mean) ** 2 for v in values)
    return 0.0 if den == 0 else num / den


def max_drawdown(equity: Sequence[float]) -> tuple[float, int]:
    peak = equity[0] if equity else 0.0
    worst = 0.0
    duration = 0
    current = 0
    for value in equity:
        if value >= peak:
            peak = value
            current = 0
        else:
            current += 1
            duration = max(duration, current)
        if peak > 0:
            worst = max(worst, 1.0 - value / peak)
    return worst, duration


def expected_shortfall(returns: Sequence[float], alpha: float = 0.05) -> float:
    if not returns:
        return 0.0
    ordered = sorted(returns)
    cutoff = max(1, int(len(ordered) * alpha))
    tail = ordered[:cutoff]
    return sum(tail) / len(tail)


def compute_metrics(
    snapshots: Sequence[PortfolioSnapshot],
    trades: Sequence[TradeRecord],
    initial_equity: float,
    timeframe: str = "D1",
    total_costs: float = 0.0,
    spread_slippage_costs: float = 0.0,
    financing_costs: float = 0.0,
    commissions: float = 0.0,
) -> MetricsBundle:
    bundle = MetricsBundle()
    if not snapshots:
        bundle.values["bars"] = 0
        return bundle

    equity = [s.equity for s in snapshots]
    final = equity[-1]
    rets = _returns(equity)
    periods = PERIODS_PER_YEAR.get(timeframe, 252)

    total_return = (final / initial_equity - 1.0) if initial_equity else 0.0
    log_growth = math.log(final / initial_equity) if final > 0 and initial_equity > 0 else float("-inf")
    years = len(equity) / periods if periods else 0.0
    cagr = ((final / initial_equity) ** (1 / years) - 1.0) if years > 0 and final > 0 else 0.0

    sd = _stdev(rets)
    mean_ret = sum(rets) / len(rets) if rets else 0.0
    sharpe = (mean_ret / sd * math.sqrt(periods)) if sd > 0 else 0.0
    downside = [r for r in rets if r < 0]
    dsd = _stdev(downside) if len(downside) > 1 else 0.0
    sortino = (mean_ret / dsd * math.sqrt(periods)) if dsd > 0 else 0.0

    mdd, dd_duration = max_drawdown(equity)
    calmar = (cagr / mdd) if mdd > 0 else 0.0

    wins = [t for t in trades if t.net_pnl > 0]
    losses = [t for t in trades if t.net_pnl < 0]
    avg_win = sum(t.net_pnl for t in wins) / len(wins) if wins else 0.0
    avg_loss = abs(sum(t.net_pnl for t in losses) / len(losses)) if losses else 0.0

    bars_in_market = sum(1 for s in snapshots if s.position is not None)
    turnover = sum(t.units * t.entry_price for t in trades)

    bundle.values.update(
        {
            "initial_equity": initial_equity,
            "final_equity": final,
            "total_return": total_return,
            "log_growth": log_growth,
            "cagr": cagr,
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": mdd,
            "max_drawdown_duration_bars": dd_duration,
            "calmar": calmar,
            "trade_count": len(trades),
            "hit_rate": (len(wins) / len(trades)) if trades else 0.0,
            "payoff_ratio": (avg_win / avg_loss) if avg_loss > 0 else 0.0,
            "avg_win": avg_win,
            "avg_loss": -avg_loss,
            "expected_shortfall_5pct": expected_shortfall(rets),
            "time_in_market_pct": bars_in_market / len(snapshots),
            "turnover_notional": turnover,
            "total_costs": total_costs,
            "spread_slippage_costs": spread_slippage_costs,
            "commissions": commissions,
            "financing_costs": financing_costs,
            "cost_drag_pct_of_initial": (total_costs / initial_equity) if initial_equity else 0.0,
            "gross_return": total_return + (total_costs / initial_equity if initial_equity else 0.0),
            "max_leverage_used": max((s.leverage for s in snapshots), default=0.0),
            "max_margin_used": max((s.margin_used for s in snapshots), default=0.0),
            "final_state": snapshots[-1].state.value,
            "bars": len(snapshots),
        }
    )
    bundle.disclosures.update(
        {
            "sharpe_frequency": timeframe,
            "sharpe_periods_per_year": periods,
            "sharpe_annualised": True,
            "return_autocorrelation_lag1": autocorrelation_lag1(rets),
            "sample_bars": len(equity),
            "sample_years_approx": round(years, 3),
            "note": (
                "Sharpe/Sortino are annualised from a finite sample and are not "
                "corrected for serial correlation or multiple testing. Deflated "
                "Sharpe and PBO require the experiment registry trial count."
            ),
        }
    )
    return bundle


def equity_curve_rows(snapshots: Sequence[PortfolioSnapshot]) -> list[tuple[datetime, float]]:
    return [(s.timestamp, s.equity) for s in snapshots]
