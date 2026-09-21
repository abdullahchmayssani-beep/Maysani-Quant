# ADR 0003 — Provider-independent, point-in-time market data (V0.2)

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

V0.1 shipped one concrete `MarketDataSource`: `CsvMarketDataSource`, which reads
a pre-built CSV (synthetic fixture or a manually supplied file) and never
contacts a network. V0.2's milestone is a real, licensed EUR/USD dataset. The
first research provider decision (made externally) is Dukascopy, tick-level
historical bid/ask. Section 23 leaves licensing/redistribution unverified, and
CLAUDE.md forbids depending on any one vendor from the rest of the system and
forbids committing raw licensed data to git.

This ADR fixes the boundary between "a provider" and "everything else" before
any Dukascopy-specific code is written, and fixes the exact pipeline stage
order, since a later provider (a different historical vendor, or eventually a
live feed) must be able to implement the same contract with zero changes
downstream of it.

## Decision

### 1. Pipeline stages are explicit and one-directional

```
FETCH -> RAW STORE -> PARSE -> NORMALIZE -> CANONICAL VALIDATE -> CANONICAL STORE
```

- **FETCH**: a `MarketDataProvider` retrieves the provider's native artifact
  (e.g. one Dukascopy `.bi5` hour file) as raw bytes. It does not parse.
- **RAW STORE**: the artifact is written verbatim to a local, content-addressed,
  immutable cache (`data/raw/...`, gitignored) before anything inspects its
  contents, alongside a manifest recording: raw bytes' SHA-256, provider
  name/version, requested instrument and window, retrieval timestamp, and the
  request that produced it. This exists so a parsing bug is always
  recoverable by re-running the pipeline against the same bytes, and so raw
  fidelity (tick-level, provider-native) is never lost to an early parse.
- **PARSE**: the *same* provider adapter turns raw bytes into structured
  ticks in provider-declared units (this is the only place Dukascopy's byte
  layout is known).
- **NORMALIZE**: provider-agnostic code aggregates ticks into canonical
  `MarketBar`s on a configured timeframe, applying a documented
  `available_time` policy (never inferring one).
- **CANONICAL VALIDATE**: provider-agnostic, severity-aware checks
  (VALID/WARNING/INVALID) on the canonical bars only. This is a different
  function from V0.1's `data.validation.validate_bars`, which stays untouched
  and keeps governing the CSV path.
- **CANONICAL STORE**: validated bars are cached locally (`data/cache/...`,
  gitignored) keyed by a reproducible identity hash (ADR-detailed below).

Raw-artifact validation (checksum match, decompressibility, structural
sanity) is a check on the FETCH/PARSE boundary, not on `MarketBar`s, and is
kept in its own module so a corrupt download is diagnosed before it can
masquerade as a data-quality problem in canonical validation.

### 2. `MarketDataProvider` is a two-method contract, not a one-shot iterator

Rejecting the earlier draft's `fetch_raw() -> Iterator[RawRecord]`: that
signature forces parsing to happen during fetch, which would discard the
original artifact bytes exactly where they are most valuable (Dukascopy's
`.bi5` files are the licensed, verifiable, redistributable-or-not unit; a
parsed record is not). The contract is instead:

```python
class MarketDataProvider(Protocol):
    provider_name: str
    provider_version: str
    def fetch_artifacts(instrument, start, end) -> Iterator[RawArtifact]: ...
    def parse_artifact(artifact: RawArtifact) -> Iterator[ProviderTick]: ...
```

`RawArtifact` carries the bytes plus everything RAW STORE needs to write its
manifest. `ProviderTick` (instrument, timestamp UTC, bid, ask, bid_volume,
ask_volume) is the one provider-agnostic shape every adapter must produce
from PARSE; unit/scale conversion (e.g. Dukascopy's per-instrument integer
point value) happens inside `parse_artifact`, never downstream.

### 3. Canonical domain object is unchanged: no `MarketBar.provider` field

`MarketBar` already separates `end_time` (event time) from `available_time`
(publication time) — Section 9.1's requirement is already satisfied by the
V0.1 schema. Provider identity is dataset-level provenance (which manifest
produced this cache), not a per-bar trading-domain concern, and `MarketBar`
already has a free-text `source` field for exactly this ("csv:filename.csv"
today, "dukascopy:<canonical_identity_hash[:12]>" for V0.2). Adding a
dedicated field would duplicate what the raw/canonical manifests already
give with full traceability, for no concrete downstream consumer. If a real
requirement appears (e.g. a strategy needing to condition on provider), add
the field then, with an ADR update.

### 4. Tick-to-bar aggregation policy (documented, not fabricated)

Dukascopy ticks are aggregated into `MarketBar`s on the run's configured
timeframe:

- `open/high/low/close` are computed from **mid price** `(bid+ask)/2` across
  ticks in the window — consistent with V0.1's existing `price_kind:
  midpoint` convention used by features.
- `bid_close`/`ask_close` are the last tick's bid/ask in the window;
  `spread = ask_close - bid_close`. This is strictly better fidelity than
  V0.1's synthetic/CSV path, which usually has no true bid/ask.
- `volume` is the summed bid+ask tick volume in the window (Dukascopy's
  reported volume units; not independently verified against a live feed in
  this session — see Known limitations).
- `available_time` uses the same `bar_close` policy V0.1's CSV loader
  defaults to: a bar becomes available at its own `end_time`. This is a
  **policy choice** carried over from V0.1, not a claim about Dukascopy's
  real publication latency, which this session could not verify (no network
  access to Dukascopy from the execution sandbox — see STATUS.md).

### 5. Quality severity: VALID / WARNING / INVALID

Canonical validation classifies every issue found into one of three
severities and the dataset overall carries the worst severity present:

| Flag | Severity | Rationale |
|---|---|---|
| `OK`, `SYNTHETIC` | VALID | informational only |
| `WEEKEND_GAP` | VALID | expected FX market closure, not a defect |
| `SUSPICIOUS_GAP` | WARNING | usable but worth surfacing in the report |
| `DUPLICATE_TIMESTAMP`, `OUT_OF_ORDER`, `INCONSISTENT_OHLC`,
  `NEGATIVE_SPREAD`, `NON_FINITE`, `TIMEZONE_NAIVE` | INVALID | cannot be
  silently repaired or guessed |

An INVALID dataset sets `validation.ok = False`, which the existing CLI gate
(`cli.py`'s `backtest` command already refuses to run on `not
source.validation.ok` unless `--allow-bad-data`) blocks on exactly as it does
today for the CSV path — no new gate mechanism, the existing one is reused.

### 6. Weekend-gap detection is a fixed heuristic, not a trading calendar

A gap is classified `WEEKEND_GAP` if it falls inside the interbank FX
convention window (Friday 21:00 UTC – Sunday 21:00 UTC); any other gap wider
than a configurable multiple of the expected tick/bar spacing is
`SUSPICIOUS_GAP`. **Known limitation:** this has no holiday calendar and no
broker-specific session table; a market holiday will currently surface as a
`SUSPICIOUS_GAP` (WARNING), not silently as `OK`. This is intentional given
V0.2 scope discipline (no over-engineering) — a full calendar is deferred
until a concrete need appears.

### 7. Reproducible canonical identity

```
canonical_identity_hash = stable_hash({
    raw_artifact_hashes: sorted [...],
    provider, provider_version,
    instrument, requested_start, requested_end,
    schema_version, normalization_policy,
})
```

Retrieval timestamp is recorded in the manifest as provenance but excluded
from the hash: re-running the same pipeline over the same raw bytes must
reproduce the same canonical dataset identity, per the existing V0.1
convention that `data_hash` folds in exactly the things that can change a
result (`docs/adr/0002`).

### 8. Point-in-time invariant is restated, not weakened

The canonical store may (and for a real historical dataset, will) contain
bars whose `available_time` is later than an earlier backtest decision time —
that is simply what "a historical archive" means. The invariant has always
been, and remains: **at decision time `t`, downstream code can access only
information whose `available_time <= t`**, enforced by `PointInTimeView`
exactly as in V0.1. Nothing about a richer canonical store changes that
enforcement point. New adversarial tests place bars with `available_time` far
in the future directly into the canonical store and prove they remain
invisible through `PointInTimeView` at an earlier `as_of` (see
`tests/unit/test_market_data_service.py`).

### 9. `configs/v0_1.yaml` is not touched

`configs/v0_2.yaml` is new. `AppConfig`/`load_config` gain an optional
`data.provider` key that defaults to `csv` (V0.1's exact current behaviour)
so `v0_1.yaml`'s absence of that key is unaffected. `backtest/runner.py`'s
`build_source` dispatches on it; nothing downstream of `build_source` needs
to know which branch ran.

## Consequences

- A second historical provider, or eventually a live feed, is a new
  `data/providers/<name>.py` module implementing `MarketDataProvider` plus a
  `provider_version` bump; `NORMALIZE`, `CANONICAL VALIDATE`, `CANONICAL
  STORE`, `MarketDataService`, and everything in `features/`, `strategies/`,
  `risk/`, `execution/`, `portfolio/`, `backtest/` are untouched.
- Raw Dukascopy bytes never enter git; only the (also gitignored) canonical
  cache and its manifests exist locally, per CLAUDE.md's "never commit
  licensed market data" rule.
- Because this session's sandboxed network egress denies
  `datafeed.dukascopy.com` (see `docs/STATUS.md`), the Dukascopy adapter is
  built and tested entirely offline against small, hand-constructed fixture
  bytes in the same binary shape as a `.bi5` file. A real fetch has not been
  proven end-to-end in this session; that is recorded as the next blocker.
