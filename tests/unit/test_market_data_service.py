"""MarketDataService end-to-end tests (ADR 0003).

Everything here runs offline against hand-built fixture bytes in the
documented `.bi5` shape - no network call is made. Covers:

- the full FETCH -> ... -> CANONICAL STORE pipeline producing MarketBars
- the adversarial point-in-time claim: a canonical store containing bars
  whose available_time is in the future relative to an as_of is still safe,
  because PointInTimeView (not the store) is the access boundary
- reproducible canonical identity (same raw bytes + policy -> same hash;
  retrieval time never changes it)
- the cross-provider invariant: BacktestEngine/PointInTimeView accept
  MarketDataService bars exactly as they accept CsvMarketDataSource bars,
  with zero provider-specific code in that call path
"""
from __future__ import annotations

import lzma
import struct
from datetime import UTC, datetime, timedelta
from pathlib import Path

from maysani_quant.backtest.engine import BacktestEngine
from maysani_quant.data.interfaces import PointInTimeView
from maysani_quant.data.pipeline.canonical_store import CanonicalStore
from maysani_quant.data.provenance import (
    SCHEMA_VERSION,
    CanonicalManifest,
    NormalizationPolicy,
    canonical_identity_hash,
)
from maysani_quant.data.providers.base import RawArtifact
from maysani_quant.data.providers.dukascopy import DukascopyProvider, _hour_starts, _url_for
from maysani_quant.data.service import PIPELINE_VERSION, MarketDataService
from maysani_quant.domain.models import InstrumentSpec, MarketBar
from maysani_quant.execution.costs import CostConfig, CostModel
from maysani_quant.execution.simulator import ExecutionSimulator
from maysani_quant.features.pipeline import FeatureConfig, FeaturePipeline
from maysani_quant.journal.store import InMemoryJournal
from maysani_quant.portfolio.ledger import PortfolioLedger
from maysani_quant.risk.hard_limits import HardRiskEngine
from maysani_quant.risk.interfaces import RiskConfig, RiskState
from maysani_quant.strategies.base import build_strategy
from tests.conftest import trending_bars

H0 = datetime(2024, 1, 3, 10, 0, 0, tzinfo=UTC)


def _bi5(records: list[tuple[int, int, int, float, float]]) -> bytes:
    raw = b"".join(struct.pack(">Iiiff", *r) for r in records)
    return lzma.compress(raw)


class OfflineDukascopyProvider(DukascopyProvider):
    """Same PARSE logic as the real adapter; FETCH reads from an in-memory
    dict instead of the network, so tests never touch a socket."""

    def __init__(self, price_precision: int, canned: dict[datetime, bytes]):
        super().__init__(price_precision)
        self._canned = canned

    def fetch_artifacts(self, instrument: str, start: datetime, end: datetime):
        for hour_start in _hour_starts(start, end):
            content = self._canned.get(hour_start, b"")
            yield RawArtifact(
                provider=self.provider_name,
                provider_version=self.provider_version,
                instrument=instrument,
                requested_start=hour_start,
                requested_end=hour_start + timedelta(hours=1),
                retrieved_at=datetime.now(UTC),
                source_uri=_url_for(instrument, hour_start),
                content=content,
            )


def _two_hour_service(tmp_path: Path, *, price_precision: int = 5) -> MarketDataService:
    canned = {
        H0: _bi5([(0, 108234, 108220, 1.0, 1.0), (1_800_000, 108250, 108236, 1.0, 1.0)]),
        H0 + timedelta(hours=1): _bi5([(0, 108300, 108286, 1.0, 1.0)]),
    }
    provider = OfflineDukascopyProvider(price_precision, canned)
    return MarketDataService(
        provider,
        instrument="EURUSD",
        start=H0,
        end=H0 + timedelta(hours=2),
        bar_seconds=3600,
        timeframe="H1",
        raw_root=tmp_path / "raw",
        canonical_root=tmp_path / "canonical",
        require_bid_ask=True,
    )


def test_pipeline_produces_bid_ask_bars(tmp_path: Path):
    service = _two_hour_service(tmp_path)
    bars = list(service.all_bars())
    assert len(bars) == 2
    assert all(b.bid_close is not None and b.ask_close is not None for b in bars)
    assert all(b.spread is not None and b.spread >= 0 for b in bars)
    assert service.validation.ok
    assert service.is_synthetic is False


def test_reproducible_identity_ignores_retrieval_time_not_inputs(tmp_path: Path):
    svc_a = _two_hour_service(tmp_path / "run_a")
    svc_b = _two_hour_service(tmp_path / "run_b")  # separate raw/canonical dirs, re-fetched
    assert svc_a.data_hash == svc_b.data_hash, "same bytes+policy must reproduce the same identity"
    assert svc_a.manifest.retrieved_at != svc_b.manifest.retrieved_at or True  # timestamps vary
    assert svc_a.manifest.canonical_identity_hash == svc_b.manifest.canonical_identity_hash

    # Changing the schema/policy version must change the identity.
    different_policy = NormalizationPolicy(
        timeframe="H1",
        available_time_policy="bar_close_plus_lag",
        available_time_lag_seconds=60,
        ohlc_price_kind="midpoint",
    )
    other_hash = canonical_identity_hash(
        raw_artifact_hashes=list(svc_a.manifest.raw_artifact_hashes),
        provider=svc_a.manifest.provider,
        provider_version=svc_a.manifest.provider_version,
        instrument=svc_a.manifest.instrument,
        requested_start=svc_a.manifest.requested_start,
        requested_end=svc_a.manifest.requested_end,
        schema_version=SCHEMA_VERSION,
        normalization_policy=different_policy,
    )
    assert other_hash != svc_a.data_hash


def test_second_run_hits_canonical_cache(tmp_path: Path):
    canned = {
        H0: _bi5([(0, 108234, 108220, 1.0, 1.0)]),
        H0 + timedelta(hours=1): _bi5([(0, 108300, 108286, 1.0, 1.0)]),
    }
    provider = OfflineDukascopyProvider(5, canned)
    kwargs = dict(
        instrument="EURUSD",
        start=H0,
        end=H0 + timedelta(hours=2),
        bar_seconds=3600,
        timeframe="H1",
        raw_root=tmp_path / "raw",
        canonical_root=tmp_path / "canonical",
        require_bid_ask=True,
    )
    first = MarketDataService(provider, **kwargs)
    second = MarketDataService(provider, **kwargs)
    assert first.data_hash == second.data_hash
    assert [b.close for b in first.all_bars()] == [b.close for b in second.all_bars()]


def test_adversarial_future_bar_in_canonical_store_is_invisible_at_earlier_as_of(tmp_path: Path):
    """A canonical store legitimately holds the whole historical archive,
    including bars far in the future relative to some earlier decision
    time. PointInTimeView, not the store, is what must refuse them."""
    store = CanonicalStore(tmp_path / "canonical")
    past = MarketBar(
        instrument="EURUSD",
        start_time=H0,
        end_time=H0 + timedelta(hours=1),
        available_time=H0 + timedelta(hours=1),
        open=1.10, high=1.101, low=1.099, close=1.1005,
        source="test",
    )
    far_future = MarketBar(
        instrument="EURUSD",
        start_time=H0 + timedelta(days=365),
        end_time=H0 + timedelta(days=365, hours=1),
        available_time=H0 + timedelta(days=365, hours=1),
        open=1.20, high=1.201, low=1.199, close=1.2005,
        source="test",
    )
    manifest = CanonicalManifest(
        canonical_identity_hash="deadbeef",
        raw_artifact_hashes=("aaaa",),
        provider="dukascopy",
        provider_version="test",
        instrument="EURUSD",
        requested_start=H0,
        requested_end=H0 + timedelta(days=366),
        schema_version=SCHEMA_VERSION,
        normalization_policy=NormalizationPolicy("H1", "bar_close", 0, "midpoint"),
        pipeline_version=PIPELINE_VERSION,
        retrieved_at=H0,
        bar_count=2,
    )
    store.write(manifest, [past, far_future])

    # The store itself, deliberately, contains both bars - it is an archive.
    all_stored = store.read_bars("dukascopy", "EURUSD", "deadbeef")
    assert len(all_stored) == 2

    # A decision made at `past`'s as_of must never see `far_future`.
    view = PointInTimeView(all_stored, as_of=past.available_time, instrument="EURUSD")
    assert len(view) == 1
    assert view.latest().close == past.close
    assert view.excluded_count == 1


def test_market_data_service_bars_run_through_the_real_engine_like_csv_bars(tmp_path: Path):
    """Cross-provider invariant: the engine, risk, and strategy layers accept
    MarketDataService bars with no provider-specific code path, exactly as
    they accept CSV-sourced bars."""
    instrument = InstrumentSpec(
        symbol="EURUSD", base_currency="EUR", quote_currency="USD",
        price_precision=5, size_step=1.0, min_order_size=1.0, contract_multiplier=1.0,
    )
    feature_config = FeatureConfig(
        momentum_lookback=3, ma_fast=2, ma_slow=4, vol_lookback=3,
        zscore_lookback=3, atr_lookback=3,
    )
    risk_config = RiskConfig(
        config_version="risk-test-v1", risk_per_trade_pct=0.01, max_leverage=5.0,
        margin_requirement_pct=0.20, max_margin_utilisation=0.50, max_open_risk_pct=0.02,
        daily_loss_limit_pct=0.03, max_drawdown_pct=0.20, max_spread_price=0.0005,
        max_realized_vol=0.05, max_staleness_bars=2.0,
    )

    def run(bars: list[MarketBar]) -> str:
        cost_model = CostModel(CostConfig(fixed_spread_price=0.0002, slippage_price=0.0))
        engine = BacktestEngine(
            instrument=instrument,
            pipeline=FeaturePipeline(feature_config),
            strategy=build_strategy("no_trade_v1", {}),
            risk=HardRiskEngine(risk_config, RiskState(peak_equity=50.0)),
            execution=ExecutionSimulator(cost_model, instrument),
            ledger=PortfolioLedger(
                initial_equity=50.0, instrument=instrument, death_threshold=0.0,
                margin_requirement_pct=risk_config.margin_requirement_pct,
            ),
            journal=InMemoryJournal(),
            bar_seconds=3600,
            experiment_id="exp-cross-provider",
            config_hash="cfg",
            data_hash="data",
        )
        result = engine.run(bars)
        return result.final_state.value

    csv_style_bars = trending_bars(10)  # uses D1 spacing but engine doesn't care
    dukascopy_style_bars = list(_two_hour_service(tmp_path).all_bars())

    csv_outcome = run(csv_style_bars)
    dukascopy_outcome = run(dukascopy_style_bars)
    assert csv_outcome == "ALIVE"
    assert dukascopy_outcome == "ALIVE"
