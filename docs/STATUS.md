# Status

Fresh-session handoff summary. Keep this current, keep it short — detail
belongs in the master reference or in code/tests, not here.

## Current version

**V0.1 — complete and frozen baseline** (`configs/v0_1.yaml` verified
byte-for-byte unchanged; CSV/synthetic path re-verified end-to-end after
every V0.2 change).

**V0.2 — provider-independent market data pipeline implemented and validated
against real Dukascopy EUR/USD data.** The real-data sample came in through
a manual CSV-export validation fixture/input path (ADR 0004), not through
automated acquisition - the automated `.bi5` network fetch remains untested
against real bytes and is the current blocker (egress denied in this
sandbox). See `docs/adr/0003-provider-independent-market-data.md` and
`docs/adr/0004-parse-stage-artifact-groups.md` for the design, and "V0.2
status" below for exactly what is and isn't proven.

## Branch / commit

- Branch: `claude/import-maysani-quant-v0.1-qs5b4f`
- HEAD: `5f368988728ed8d12d3b0b9cddf6068af3655b8b`
  ("Lint: apply safe ruff fixes; pin str-Enum rationale")
- Prior commit: `9e9f031` ("V0.1 scaffold")
- History was imported from the original V0.1 development environment via a
  git bundle, preserving the original commit hashes.

## V0.1 validation (last run at repository-governance commit)

- `pytest`: **88 passed**, 0 failed
- `pytest -m invariant`: **45/88** tests collected as invariant-tagged
- `ruff check .`: clean, no findings
- `maysani-quant` CLI installs and runs (`backtest`, `validate-data`,
  `show-experiment`, `strategies`, `make-synthetic-dataset`)

## V0.1 major capabilities

- Deterministic, event-driven backtest engine enforcing point-in-time data
  access (`available_time <= as_of`), see `src/maysani_quant/backtest/engine.py`.
- Fixed authority chain: `features/strategies -> risk/hard_limits ->
  execution/simulator -> portfolio/ledger` (propose -> permit -> mutate ->
  record). See `CLAUDE.md` and `docs/adr/0001-authority-boundaries.md`.
- Hard-coded, config-driven risk engine (`risk/hard_limits.py`) — the only
  code path that can size an order.
- Simulated execution with realistic fill timing (next-bar open), spread/side
  correctness (buys at ask, sells at bid), and conservative resolution of
  ambiguous intrabar paths.
- Append-only journal (idempotent replay, no duplicate fills on restart) and
  an immutable experiment registry (no deletion of failed trials).
- Two baseline strategies (momentum, mean-reversion) plus no-trade and
  buy-and-hold controls, all running against USD 50.00 simulated equity on
  EUR/USD only.
- No LLM dependency anywhere in the pipeline; `tests/regression` fails the
  build if one is imported.
- `docs/MAYSANI_QUANT_MASTER_REFERENCE.md` (+ `.docx`) is the full design
  dossier; `docs/adr/` holds the two accepted architecture decisions.

## Known finding (not a bug — do not "fix" by tuning)

Under the provisional V0.1 defaults, at USD 50.00 starting equity the
**margin gate binds before the 1% risk budget** (~113 vs ~119 units). This is
pinned by `test_margin_gate_binds_before_risk_budget_at_fifty_dollars` and is
data for the Section 23 feasibility question, not something to tune away.

## Known discrepancy (informational)

The handoff description that accompanied the V0.1 import mentioned
approximately 92 files; the imported git history contains **68 tracked
files**. All other integrity checks (2 commits, 88 tests, 45 invariant tests,
clean lint, working CLI, Master Reference present) matched exactly, and the
git bundle verified as a complete history with no corruption. This is noted
for awareness, not treated as a defect.

## V0.2 status (this session)

**Architecture implemented, offline-tested, and validated against real
Dukascopy EUR/USD data via a manual CSV-export validation fixture (ADR
0004) - automated `.bi5` network acquisition is still untested and remains
the current blocker.** See `docs/adr/0003-provider-independent-market-data.md`
for the full design. Summary:

- New pipeline: `data/providers/` (provider contract + Dukascopy bi5
  adapter), `data/pipeline/` (raw_store, raw_validate, normalize,
  canonical_validate, canonical_store), `data/provenance.py` (manifests +
  reproducible identity hash), `data/service.py` (`MarketDataService`).
- `configs/v0_1.yaml` is untouched (byte-for-byte, verified via `git diff`
  before every commit). `configs/v0_2.yaml` is new and exercises
  `data.provider: dukascopy`.
- `backtest/runner.py::build_source` dispatches on `config.data_provider`;
  the CSV/synthetic path is unchanged and re-verified end-to-end
  (`validate-data`/`backtest --config configs/v0_1.yaml` after every batch).
- 114 tests pass (was 88; +25 new tests, +1 net from splitting one
  regression test - see "Test suite change" below), `pytest -m invariant`
  47 pass (was 45), `ruff check .` clean.
- **Real-data validation: done, via a manual validation fixture/input path,
  not via automated acquisition.** `datafeed.dukascopy.com:443` (the `.bi5`
  network fetch - the intended automated acquisition mechanism) is still
  denied by this sandbox's egress policy (403 on CONNECT, confirmed via the
  proxy's status endpoint) and **cannot be tested in this sandbox** because
  of that egress restriction. The user instead supplied a real Dukascopy
  **website CSV export** (EUR/USD BID+ASK, 2026-09-17 12:00-13:00 UTC, 5293
  rows/side) as a manually-downloaded validation sample. ADR 0004 adds
  `data/providers/dukascopy_csv_export.py` for this purpose (FETCH reads
  local files instead of the network; everything downstream - RAW STORE,
  PARSE, NORMALIZE, CANONICAL VALIDATE, CANONICAL STORE - is unchanged).
  **This adapter is a validation fixture/input path, not the long-term
  acquisition mechanism** - it requires a human to download every window by
  hand and does not scale to a real backtest dataset (see ADR 0004's
  "Scope" section). The sample has been run through the full pipeline end
  to end and validated (see "Real-data validation results" below); the raw
  CSVs and everything derived from them live only in the gitignored
  `data/raw/` and `data/cache/` and were never committed.
- **Current blocker: automatic (`.bi5`) data acquisition.** That half of
  ADR 0003's original scope remains blocked by this sandbox's egress
  policy; `configs/v0_2.yaml`'s `data.provider: dukascopy` window has not
  been fetched, and cannot be, from this environment. The $50/margin
  feasibility question (Section 23) has not been re-examined with a dataset
  large enough to run a strategy against (one hour of M1 bars is enough to
  validate the pipeline, not to backtest).

### Real-data validation results (2026-09-17 12:00-13:00 UTC EUR/USD sample)

Ingested via `DukascopyCsvExportProvider` -> `MarketDataService` (M1
timeframe, `require_bid_ask=True`), exactly as any other provider would be:

- **Pairing/alignment:** verified, not assumed - both files have identical
  row counts (5293) and identical timestamps at every row index; pairing by
  index then gives `ask >= bid` at all 5293 rows and a realistic spread
  distribution (mostly 0.1-1.5 pips). See ADR 0004 for the full check.
- **Canonical bars:** 60 M1 bars, zero data-quality issues
  (`validation.severity == VALID`).
- **Volume conservation:** sum of all raw tick volumes (bid+ask,
  19,742,370,000 raw units) exactly equals the sum of canonical bar volumes
  - the tick-to-bar aggregation is lossless.
- **PIT behaviour:** `PointInTimeView` at an as_of mid-sample correctly
  exposed only the bars up to and including that point and excluded the
  rest, on this real dataset (not just the earlier synthetic/fixture
  adversarial test).
- **Provenance/reproducibility:** two raw artifacts stored and
  checksum-verified (labelled `bid`/`ask` in their manifests); re-running
  the identical ingestion reproduces the identical `canonical_identity_hash`.
- **Bug found and fixed:** `CanonicalManifest.actual_start` was computed from
  the first bar's `end_time` instead of its `start_time`, silently reporting
  the coverage window as starting one bar-length later than it actually did.
  Fixed, with a regression assertion added.
- **Fidelity limitation confirmed on real data:** the website export's
  timestamps are 1-second resolution (up to 12 ticks share one timestamp in
  this sample), versus `.bi5`'s millisecond resolution - immaterial to M1/H1
  bar aggregation, but this ingestion path could never support a genuine
  tick-level backtest.
- **Volume units:** still `[UNVERIFIED]` against Dukascopy's own
  documentation; the raw values (e.g. 900000, 1800000) are consistent with
  "volume in millions of base currency x 1,000,000" but this adapter passes
  them through unscaled rather than asserting that interpretation.

### Test suite change (flagged, not silent)

`tests/regression/test_regression.py::test_no_llm_or_network_dependency_in_v0_1`
forbade `urllib.request` (and `requests`/`httpx`) anywhere in
`src/maysani_quant/`. That blanket rule was a V0.1-era byproduct of V0.1
having zero network I/O by scope, not the named invariant itself (CLAUDE.md's
actual "Never" is "no LLM dependency"). V0.2's externally-approved Dukascopy
adapter needs to make real HTTP requests, by design. The test is now split:
`test_no_llm_dependency_anywhere` (unconditional, everywhere, unchanged in
strength) and `test_no_network_dependency_outside_the_provider_boundary`
(unconditional everywhere **except** `data/providers/`, the one ADR
0003-sanctioned adapter boundary). This is a narrowing of an
over-broad implementation detail to match the now-explicit architecture, not
a loosening of the LLM invariant; both new tests pass and the LLM check is
identical in scope to before.

### Known limitations recorded in ADR 0003 (not defects)

- Dukascopy's `.bi5` byte format is documented from public open-source-tool
  knowledge, not from Dukascopy's own docs (this session cannot reach
  `datafeed.dukascopy.com` to verify) - marked `[UNVERIFIED]` in
  `data/providers/dukascopy.py`'s module docstring until a real `.bi5` fetch
  confirms it. (The website CSV export path, by contrast, **has** now been
  validated against a real sample - see above.)
- Weekend-gap detection is a fixed Fri 21:00 UTC-Sun 21:00 UTC heuristic,
  not a holiday/session calendar; a market holiday will surface as
  `SUSPICIOUS_GAP` (WARNING), not silently as OK.
- Re-running `MarketDataService` always re-fetches raw artifacts over the
  network (or re-reads local files, for the CSV export path); only the
  final canonical-store write is cache-idempotent (no per-window
  "already fetched" index yet).
- The website CSV export's 1-second timestamp resolution and its
  `[UNVERIFIED]` volume units (see above) are this ingestion path's own
  limitations, distinct from `.bi5`'s.

## Current blocker

**Automatic (`.bi5` network) data acquisition.** This sandbox's egress
policy denies `datafeed.dukascopy.com:443` (403 on CONNECT, confirmed via
the proxy's status endpoint) - `.bi5` network acquisition **cannot be
tested in this sandbox** because of that egress restriction, so the `.bi5`
provider remains untested against real bytes and `configs/v0_2.yaml`'s
declared one-week window has not been fetched. The website-CSV-export path
(ADR 0004) is not blocked and has been validated end to end against real
data, but it is a manual validation fixture/input path only - it requires a
human to download every window by hand, one export at a time, and does not
substitute for `.bi5` at any real acquisition scale. The next step (either
get network access for `.bi5`, or manually assemble enough CSV exports to
run the frozen strategies against a real multi-day dataset and report
results, per the approved V0.2 plan) has not been done.
