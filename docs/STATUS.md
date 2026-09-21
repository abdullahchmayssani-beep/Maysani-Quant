# Status

Fresh-session handoff summary. Keep this current, keep it short — detail
belongs in the master reference or in code/tests, not here.

## Current version

**V0.1 — complete and frozen baseline** (`configs/v0_1.yaml` verified
byte-for-byte unchanged; CSV/synthetic path re-verified end-to-end after
every V0.2 change).

**V0.2 — provider-independent market data pipeline implemented, not yet
exercised against real data.** See `docs/adr/0003-provider-independent-market-data.md`
for the design and "V0.2 status" below for what is and isn't proven.

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

**Architecture implemented and offline-tested; not yet run against real
Dukascopy data.** See `docs/adr/0003-provider-independent-market-data.md` for
the full design. Summary:

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
- **Not yet done, and blocked in this sandbox:** fetching any real
  Dukascopy artifact. `datafeed.dukascopy.com:443` is denied by this
  session's egress policy (403 on CONNECT; confirmed via the proxy's own
  status endpoint, `recentRelayFailures`). Every test in the new suite runs
  against hand-built fixture bytes in the documented `.bi5` shape, never
  real downloaded data. `configs/v0_2.yaml`'s Dukascopy window has not been
  fetched, so **no real-data baseline exists yet** and the $50/margin
  feasibility question (Section 23) has not been re-examined with real
  spread data.

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

- Dukascopy's byte format is documented from public open-source-tool
  knowledge, not from Dukascopy's own docs (this session cannot reach
  `datafeed.dukascopy.com` to verify) - marked `[UNVERIFIED]` in
  `data/providers/dukascopy.py`'s module docstring until a real fetch
  confirms it.
- Weekend-gap detection is a fixed Fri 21:00 UTC-Sun 21:00 UTC heuristic,
  not a holiday/session calendar; a market holiday will surface as
  `SUSPICIOUS_GAP` (WARNING), not silently as OK.
- Re-running `MarketDataService` always re-fetches raw artifacts over the
  network; only the final canonical-store write is cache-idempotent (no
  per-hour "already fetched" index yet).

## Current blocker

Fetching real Dukascopy data. This sandbox's egress policy denies
`datafeed.dukascopy.com:443` (403 on CONNECT). The full pipeline is built
and tested offline; the next step (prove it on a small real sample, then run
the frozen strategy against a real dataset and report results, per the
approved V0.2 plan) requires network access this session does not have.
`configs/v0_2.yaml` is ready to run as soon as that access exists.
