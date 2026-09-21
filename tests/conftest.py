"""Shared fixtures.

Test data here is explicitly constructed, never sampled from a market. Where a
test needs a price path it states the path inline so the expected result can be
computed by hand in the assertion.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from maysani_quant.domain.enums import QualityFlag
from maysani_quant.domain.models import InstrumentSpec, MarketBar
from maysani_quant.execution.costs import CostConfig, CostModel
from maysani_quant.features.pipeline import FeatureConfig
from maysani_quant.risk.interfaces import RiskConfig

START = datetime(2024, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def instrument() -> InstrumentSpec:
    return InstrumentSpec(
        symbol="EURUSD",
        base_currency="EUR",
        quote_currency="USD",
        price_precision=5,
        size_step=1.0,
        min_order_size=1.0,
        contract_multiplier=1.0,
    )


def make_bar(
    index: int,
    open_px: float,
    high: float,
    low: float,
    close: float,
    spread: float | None = None,
    synthetic: bool = True,
    available_offset_seconds: int = 0,
) -> MarketBar:
    start = START + timedelta(days=index)
    end = start + timedelta(days=1)
    return MarketBar(
        instrument="EURUSD",
        start_time=start,
        end_time=end,
        available_time=end + timedelta(seconds=available_offset_seconds),
        open=open_px,
        high=high,
        low=low,
        close=close,
        volume=1000.0,
        spread=spread,
        source="test",
        quality_flags=(QualityFlag.SYNTHETIC,) if synthetic else (QualityFlag.OK,),
    )


def flat_bars(n: int, price: float = 1.10) -> list[MarketBar]:
    """A perfectly flat price series. Any P&L on this is pure cost."""
    return [make_bar(i, price, price, price, price) for i in range(n)]


def trending_bars(n: int, start_price: float = 1.10, step: float = 0.001) -> list[MarketBar]:
    bars = []
    price = start_price
    for i in range(n):
        nxt = price + step
        bars.append(
            make_bar(i, price, max(price, nxt) + 0.0002, min(price, nxt) - 0.0002, nxt)
        )
        price = nxt
    return bars


def oscillating_bars(n: int, centre: float = 1.10, amplitude: float = 0.01) -> list[MarketBar]:
    import math

    bars = []
    for i in range(n):
        open_px = centre + amplitude * math.sin(i / 5.0)
        close_px = centre + amplitude * math.sin((i + 1) / 5.0)
        bars.append(
            make_bar(
                i,
                open_px,
                max(open_px, close_px) + 0.0005,
                min(open_px, close_px) - 0.0005,
                close_px,
            )
        )
    return bars


@pytest.fixture
def zero_cost_model() -> CostModel:
    return CostModel(
        CostConfig(
            spread_model="fixed",
            fixed_spread_price=0.0,
            slippage_price=0.0,
            commission_per_unit=0.0,
            scenario_name="zero",
        )
    )


@pytest.fixture
def cost_model() -> CostModel:
    return CostModel(
        CostConfig(
            spread_model="fixed",
            fixed_spread_price=0.0002,
            slippage_price=0.00001,
            commission_per_unit=0.00005,
            scenario_name="test",
        )
    )


@pytest.fixture
def risk_config() -> RiskConfig:
    return RiskConfig(
        config_version="risk-test-v1",
        risk_per_trade_pct=0.01,
        max_leverage=5.0,
        margin_requirement_pct=0.20,
        max_margin_utilisation=0.50,
        max_open_risk_pct=0.02,
        daily_loss_limit_pct=0.03,
        max_drawdown_pct=0.20,
        max_spread_price=0.0005,
        max_realized_vol=0.05,
        max_staleness_bars=2.0,
    )


@pytest.fixture
def feature_config() -> FeatureConfig:
    return FeatureConfig(
        momentum_lookback=5,
        ma_fast=3,
        ma_slow=10,
        vol_lookback=5,
        zscore_lookback=5,
        atr_lookback=5,
    )


@pytest.fixture
def synthetic_csv(tmp_path: Path) -> Path:
    """A small SYNTHETIC dataset on disk for source/CLI tests."""
    rows = ["timestamp,open,high,low,close,volume"]
    price = 1.10
    for i in range(120):
        nxt = price * (1 + 0.0004 * ((-1) ** i) + 0.00005)
        rows.append(
            f"{(START + timedelta(days=i)).isoformat()},"
            f"{price:.5f},{max(price, nxt) + 0.0003:.5f},"
            f"{min(price, nxt) - 0.0003:.5f},{nxt:.5f},1000"
        )
        price = nxt
    path = tmp_path / "SYNTHETIC_test_eurusd_d1.csv"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path
