# CLAUDE.md

Read this first. It is short on purpose: it repeats only the rules whose
violation would be expensive. Everything else lives in
`docs/MAYSANI_QUANT_MASTER_REFERENCE.md` (source of truth for design intent)
and `docs/adr/` — this file defers to both. Git/the repository state is the
source of truth for *what currently exists*; do not trust a prior summary
over `git log`/`git status`/the working tree.

## Core principle

**AI interprets and proposes. Mathematics determines edge. Hard-coded risk
determines permission. The market determines correctness.**

## Current phase: V0.1

Scope is fixed by Section 21 of the master reference. V0.1 scope overrides the
temptation to build later phases.

- EUR/USD only, historical data only, USD 50.00 simulated equity
- BUY / SELL / WAIT; two transparent baselines plus no-trade and buy-and-hold controls
- **No LLM dependency.** `tests/regression` fails the build if one is imported.

## The authority chain — do not change without an ADR

```
features/strategies  ->  risk/hard_limits  ->  execution/simulator  ->  portfolio/ledger
     PROPOSE                 PERMIT                  MUTATE                 RECORD
```

- A strategy returns a `Signal`. It never returns a size and never sees cash.
- `HardRiskEngine.assess` is the only code that produces a size.
- `ExecutionSimulator.build_intent` is the only constructor of `OrderIntent`,
  and it raises `RiskBypassError` on any non-approving decision.
- Changing any arrow above requires a new file in `docs/adr/` first.

## Invariants with tests behind them

If one of these tests fails, the fix is in the code, never in the test.

| Invariant | Test |
|---|---|
| Features only see `available_time <= as_of` | `tests/unit/test_point_in_time.py` |
| Flat-price round trip loses exactly modelled costs | `test_accounting.py::test_flat_price_round_trip...` |
| Buys fill at ask, sells at bid, next bar open | `test_execution.py` |
| Ambiguous bars resolve adversely or are skipped | `test_execution.py::test_ambiguous_bar_*` |
| A REJECT cannot become an order | `test_risk_engine.py::test_reject_cannot_become_an_order` |
| Loss at stop never exceeds the risk budget | `test_risk_engine.py::test_loss_at_stop_*` |
| Death is terminal | `test_accounting.py::test_death_state_is_terminal` |
| Every bar journals one decision, WAIT included | `tests/integration/test_engine.py` |
| Identical inputs produce an identical journal | `test_engine.py::test_determinism_*` |
| Replay never duplicates fills | `test_engine.py::test_restart_*` |
| Reports never claim profitability | `tests/regression` |

Run them: `pytest -m invariant` (subset) or `pytest` (everything).

## Never

The full list is Section 22. The ones most likely to be violated by accident:

- Never fabricate market, macro, broker or performance data. The synthetic
  generator writes `SYNTHETIC_*` files only and every report banners them.
- Never let future information into a historical decision — including through
  rolling-window bugs, global normalisation, or revised data. Point-in-time
  integrity (`available_time <= as_of`) is never traded away for convenience.
- Never change a risk limit, death rule or cost assumption silently. They live
  in `configs/*.yaml`; changing one changes the config hash and the experiment id.
- Never change a strategy's parameters merely to make a result look better;
  a parameter change is a new experiment, not a fix.
- Never bypass the authority chain or the deterministic risk engine —
  `HardRiskEngine.assess` is the only path to a size, in code and in tests alike.
- Never delete an experiment from `runs/experiments.jsonl`. Failed trials are
  the multiple-testing denominator.
- Never disable, skip or loosen a test or invariant — including to save tokens
  or make a session go faster — to make CI green.
- Never tune a strategy against the final holdout and keep calling it a holdout.
- Never describe a result as profitable before it clears the promotion
  pipeline in Section 13.8; no claim of profitability is ever unsupported.
- Never add live-execution capability. V0.1/V0.2 are simulation-only; live
  trading requires an explicit, later promotion decision.
- Never fabricate data or silently introduce an assumption to fill a gap —
  mark it `[UNVERIFIED]` and ask instead.
- Never expose credentials or secrets (`.env.example` documents the shape of
  config, not real values; no key ever belongs in code, logs or commits).

## Known findings (do not "fix" these by tuning)

- **At USD 50 the margin gate binds before the 1% risk budget** under the
  provisional defaults (~113 vs ~119 units). Pinned by
  `test_margin_gate_binds_before_risk_budget_at_fifty_dollars`. This is data
  for the Section 23 feasibility question, not a bug.
- `buy_and_hold_v1` v1.0.0 was vetoed on every bar for lacking a stop and
  reported as a clean zero. Fixed in v1.1.0; the report now warns about any
  non-control strategy that never trades.

## Session workflow (do this on every fresh session)

1. Read `docs/STATUS.md` and `docs/REPO_MAP.md` before any broad exploration —
   they answer "what state is this in" and "where does X live" cheaper than a
   repo scan does.
2. Consult only the relevant section(s) of `docs/MAYSANI_QUANT_MASTER_REFERENCE.md`
   for the task at hand. Do not read the whole document by default.
3. Prefer targeted file reads/searches over broad directory scans; don't
   reread a file you already have unchanged content for in-session.
4. Keep command and test output bounded — grep/tail to the relevant failure
   instead of dumping full logs.
5. Run narrowly-targeted tests while iterating; run the full suite
   (`pytest`) plus `pytest -m invariant` and lint at completion/promotion
   gates, not after every small edit.
6. Don't reach for external research/web tools unless the task actually
   requires them.
7. Don't spawn subagents by default. Use one only when it materially helps
   (e.g. a large independent search), and hand it narrow, specific context.
8. Use the least expensive model/reasoning level that can do the task
   correctly; escalate only when the task's complexity justifies it.
9. Don't over-engineer, generalize, or start work that belongs to a later
   roadmap phase (see "Current phase" above).

Correctness, financial safety, reproducibility and test integrity always
outrank token/time savings — the rules above are about not wasting effort,
never about cutting a corner listed in "Never".

## Working rhythm

1. Inspect the repo state (`docs/STATUS.md`, `git log`/`git status`). Write an
   ADR before touching authority boundaries.
2. Domain models and tests before strategies. Accounting and risk before signals.
3. Every assumption goes in config and is recorded in experiment output.
4. When unsure whether a source supports a claim, mark it `[UNVERIFIED]` and
   ask — do not invent.
5. Commit coherent, tested units of work — not partial or unverified changes.
6. **End every batch by reporting:** files changed, tests run, failures,
   assumptions made, and the next promotion gate. Update `docs/STATUS.md`
   after any meaningful completed batch.
