# Repository map

Concise orientation, not a file-by-file inventory. For design rationale,
see the relevant section of `docs/MAYSANI_QUANT_MASTER_REFERENCE.md`; for
current state, see `docs/STATUS.md`.

## Top level

- `src/maysani_quant/` — the package (see below).
- `tests/` — unit, integration and regression tests.
- `configs/v0_1.yaml` — the only V0.1 config; every tunable that affects a
  result lives here and is hashed into the experiment record.
- `data/` — `SYNTHETIC_eurusd_d1.csv` (synthetic fixture) + `README.md`.
  No real market data is checked in.
- `runs/` — experiment registry output (`experiments.jsonl`) and journals.
  Append-only; nothing here is ever deleted.
- `docs/` — `MAYSANI_QUANT_MASTER_REFERENCE.md`/`.docx` (design dossier,
  source of truth for intent), `STATUS.md`, `REPO_MAP.md` (this file),
  `adr/` (architecture decision records).
- `.env.example` — documents the *shape* of any environment configuration;
  never holds real values.
- `pyproject.toml` — package metadata, the `maysani-quant` CLI entry point,
  pytest config (`markers = ["invariant: ..."]`), ruff config.

## The authority chain (package layout mirrors it)

```
features/strategies  ->  risk/hard_limits  ->  execution/simulator  ->  portfolio/ledger
     PROPOSE                 PERMIT                  MUTATE                 RECORD
```

- `domain/` — shared types with no behaviour of their own:
  - `models.py` — `InstrumentSpec`, `MarketBar`, `FeatureSnapshot`, `Signal`,
    `RiskDecision`, `OrderIntent`, `Fill`, `Position`, `PortfolioSnapshot`,
    `DecisionRecord`, `TradeRecord`, `ExperimentRecord`, plus
    `stable_hash`/`sequence_hash` used for determinism checks.
  - `enums.py` — `Action`, `Side`, `OrderType`, `FillStatus`, `Verdict`,
    `OrganismState`, `AmbiguousBarPolicy`, `QualityFlag`, `ReasonCode`.
  - `events.py` — domain event definitions.

- `data/` — market data access:
  - `interfaces.py` — `MarketDataSource` (Protocol), `PointInTimeView` (the
    only way features may read bars; enforces `available_time <= as_of`),
    `LookAheadError`, `InsufficientHistory`.
  - `csv_source.py` — the CSV-backed `MarketDataSource`; refuses to invent an
    `available_time` and refuses to treat midpoint OHLC as executable without
    an explicit spread policy.
  - `validation.py` — bar-level data validation / `ValidationReport`.

- `features/` — pure, point-in-time-safe feature computation
  (`returns.py`, `momentum.py`, `mean_reversion.py`, `volatility.py`,
  `pipeline.py` wires them into a `FeatureSnapshot`). No side effects, no
  access to cash or risk.

- `strategies/` — **PROPOSE**. `base.py` defines the strategy contract: a
  strategy returns a `Signal` (direction + score + proposed stop distance),
  never a size, never sees cash or the risk engine. `baselines.py` (no-trade,
  buy-and-hold), `momentum_v1.py`, `mean_reversion_v1.py` are the concrete
  strategies.

- `risk/` — **PERMIT**. `hard_limits.py`'s `HardRiskEngine.assess` is the
  only code in the repository that produces an order size; gate order is
  fixed (blocking gates before sizing gates). `interfaces.py` defines
  `RiskConfig`, `RiskState`, `MarketState`, `RiskPolicy`.

- `execution/` — **MUTATE**. `simulator.py`'s `ExecutionSimulator` is the
  only constructor of `OrderIntent` (raises `RiskBypassError` on any
  non-approving `RiskDecision`); enforces next-bar-open fills and
  conservative resolution of ambiguous intrabar paths. `costs.py` models
  spread/commission/slippage/financing. `models.py` holds execution-local
  types.

- `portfolio/` — **RECORD**. `ledger.py` maintains the accounting identity
  `equity = cash + unrealized_pnl`, marking unrealized P&L at the exit-side
  price, never mid.

- `backtest/` — orchestration, not authority:
  - `engine.py` — `BacktestEngine`, the per-bar event loop described in its
    module docstring (fill at open, mark at close, then
    features -> strategy -> risk -> journal).
  - `runner.py` — the single place that wires data source, features,
    strategy, risk, execution, ledger and journal together
    (`ENGINE_VERSION`, `BacktestResult`).
  - `metrics.py` — `MetricsBundle` / `compute_metrics`.
  - `report.py` — renders the human-readable run report (always banners
    synthetic data and non-trading strategies; never claims profitability).

- `journal/` — append-only decision/fill log. `store.py` guarantees
  append-only writes and idempotent replay (a record whose content hash
  already exists is not rewritten, so a restart cannot duplicate fills).
  `schema.py` defines the record shape.

- `experiments/` — `registry.py` writes an immutable `ExperimentRecord` for
  every trial before it runs and closes it with a status after (including
  FAILED/ABANDONED); no delete method exists. `schema.py` defines the
  experiment config hash / identity.

## Configuration

- `configs/v0_1.yaml` is the only config file. Every number that can
  influence a result — instrument spec, account, risk limits, cost model,
  data source — lives here and is loaded strictly (`config.py`: unknown
  keys raise). Changing a value changes the config hash and the experiment
  id; see `CLAUDE.md` → Never.

## Tests

- `tests/unit/` — `test_point_in_time.py`, `test_accounting.py`,
  `test_execution.py`, `test_risk_engine.py` — the invariant tests live here
  (see the table in `CLAUDE.md`), tagged `@pytest.mark.invariant`.
- `tests/integration/test_engine.py` — full-engine determinism, restart/replay,
  one-decision-per-bar.
- `tests/regression/test_regression.py` — repo-wide regressions, including
  the "no LLM dependency" build check.
- `tests/conftest.py` — shared fixtures.
- Run: `pytest` (full suite) or `pytest -m invariant` (invariant subset only).

## Documentation / ADRs

- `docs/MAYSANI_QUANT_MASTER_REFERENCE.md` / `.docx` — full design dossier,
  source of truth for design intent; read only the section relevant to the
  task at hand, not the whole document.
- `docs/adr/0001-authority-boundaries.md` — why the propose/permit/mutate/
  record chain is fixed.
- `docs/adr/0002-persistence-and-reproducibility.md` — why the journal and
  experiment registry are append-only.
- Any change to authority boundaries, persistence semantics or risk
  invariants requires a new ADR first.

## CLI entry point

`maysani-quant` (installed via `pyproject.toml`'s `[project.scripts]`,
implemented in `src/maysani_quant/cli.py`):

- `maysani-quant backtest --config configs/v0_1.yaml`
- `maysani-quant validate-data --config configs/v0_1.yaml`
- `maysani-quant show-experiment --id <experiment_id>`
- `maysani-quant strategies`
- `maysani-quant make-synthetic-dataset --out data/SYNTHETIC_...csv` — test
  fixture only; output is always named `SYNTHETIC_*`, flagged per-bar, and
  banner-warned in every report.
