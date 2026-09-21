# Maysani Quant — V0.1

A deterministic, falsifiable FX research engine. V0.1 exists to prove data
timing, cost accounting, risk enforcement and reproducibility **before** any
LLM, macro model or live broker is added.

> **Status:** research engine. Nothing in this repository is evidence that any
> strategy is profitable, and nothing here is an authorisation to trade real
> capital. See Section 13.8 of the master reference for the promotion pipeline.

## Install

Requires Python 3.11+.

```bash
git clone <repo> maysani-quant && cd maysani-quant
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

No API keys, no network access and no LLM are required for V0.1.

## Run

```bash
pytest                                   # full suite
pytest -m invariant                      # the non-negotiable invariants only

maysani-quant make-synthetic-dataset     # writes data/SYNTHETIC_eurusd_d1.csv
maysani-quant validate-data              # fingerprint + validation report
maysani-quant backtest                   # all configured strategies + baselines
maysani-quant backtest --strategy momentum_v1 --json runs/metrics.json
maysani-quant show-experiment --id <experiment_id>
```

`make-synthetic-dataset` produces **synthetic bars for testing the plumbing**.
They are not market data; every report run on them opens with a banner saying
so. To run on real EUR/USD, see [`data/README.md`](data/README.md).

## What a run produces

| Output | Location | Nature |
|---|---|---|
| Decision / fill / trade / portfolio journal | `runs/<run_id>.jsonl` | append-only, content-addressed |
| Restart checkpoint | `runs/<run_id>.checkpoint.json` | ledger + risk state |
| Experiment registry | `runs/experiments.jsonl` | every trial, never pruned |
| Report | `runs/report_<run_id>.txt` | measured values + assumptions |

Every `DecisionRecord` names its feature snapshot, strategy version, risk
decision, portfolio state, config hash, data hash and code version, so any
decision can be reconstructed from the journal alone.

## Layout

```
src/maysani_quant/
  domain/        frozen records, enums, reason codes
  data/          CSV source, point-in-time view, validation
  features/      rolling-only returns, momentum, mean-reversion, volatility
  strategies/    baselines + momentum_v1 + mean_reversion_v1   (PROPOSE)
  risk/          deterministic hard risk engine                (PERMIT)
  execution/     cost model + next-bar-open simulator          (MUTATE)
  portfolio/     ledger with an enforced accounting identity   (RECORD)
  backtest/      event loop, metrics, report, runner
  journal/       append-only JSONL store
  experiments/   immutable trial registry
  config.py      strict YAML loader
  cli.py
configs/v0_1.yaml   every tunable, all provisional
tests/{unit,integration,regression}
docs/            master reference + ADRs
```

## Decision timing

Features and strategy evaluate only after bar *t* is complete. The earliest
fill is the **open of bar t+1**, on the executable side (ask for buys, bid for
sells) plus configured slippage. A feature cannot read bar *t+1*; the
point-in-time view filters on `available_time`, not event time.

## Where to start reading

- `CLAUDE.md` — rules for anyone (human or agent) changing this code
- `docs/adr/` — why the structure is the way it is
- `docs/MAYSANI_QUANT_MASTER_REFERENCE.docx` — the full design dossier
