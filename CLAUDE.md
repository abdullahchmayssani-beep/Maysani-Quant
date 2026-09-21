# CLAUDE.md

Read this first. It is short on purpose: it repeats only the rules whose
violation would be expensive. Everything else lives in
`docs/MAYSANI_QUANT_MASTER_REFERENCE.docx` — the master reference is the
source of truth, and this file defers to it.

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
  rolling-window bugs, global normalisation, or revised data.
- Never change a risk limit, death rule or cost assumption silently. They live
  in `configs/*.yaml`; changing one changes the config hash and the experiment id.
- Never delete an experiment from `runs/experiments.jsonl`. Failed trials are
  the multiple-testing denominator.
- Never disable, skip or loosen a test to make CI green.
- Never tune a strategy against the final holdout and keep calling it a holdout.
- Never describe a result as profitable before it clears the promotion
  pipeline in Section 13.8.

## Known findings (do not "fix" these by tuning)

- **At USD 50 the margin gate binds before the 1% risk budget** under the
  provisional defaults (~113 vs ~119 units). Pinned by
  `test_margin_gate_binds_before_risk_budget_at_fifty_dollars`. This is data
  for the Section 23 feasibility question, not a bug.
- `buy_and_hold_v1` v1.0.0 was vetoed on every bar for lacking a stop and
  reported as a clean zero. Fixed in v1.1.0; the report now warns about any
  non-control strategy that never trades.

## Working rhythm

1. Read Sections 1–3 and 21 of the master reference before writing code.
2. Inspect the repo state. Write an ADR before touching authority boundaries.
3. Domain models and tests before strategies. Accounting and risk before signals.
4. Every assumption goes in config and is recorded in experiment output.
5. When unsure whether a source supports a claim, mark it `[UNVERIFIED]` and
   ask — do not invent.
6. **End every batch by reporting:** files changed, tests run, failures,
   assumptions made, and the next promotion gate.
