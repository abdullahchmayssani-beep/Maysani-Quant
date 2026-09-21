# ADR 0002 — Persistence and reproducibility for V0.1

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

Section 21.7 permits SQLite or append-only local files for V0.1, provided
migration to PostgreSQL stays straightforward. Section 21.9 requires
determinism, idempotent restart, and experiment ids that point to data, config
and code.

## Decision

1. **Journal:** one append-only JSONL file per run. No update or delete method
   exists. Chosen over SQLite because a text journal is diffable and cannot
   silently migrate.
2. **Content-addressed records.** A record id is `hash(run, type, payload)`.
   The sequence number is *not* in the hash. An earlier draft included it, and
   the restart test caught that a replay then duplicated every fill. Wall-clock
   `written_at` is excluded from the determinism fingerprint for the same
   reason.
3. **Experiment registry** (`runs/experiments.jsonl`) is an append-only event
   log of `OPEN` and `CLOSE` rows. Failed and abandoned trials remain. It is
   **committed to git** (see `.gitignore`), because the trial count is the
   multiple-testing denominator and must not live only on one laptop.
4. **Experiment id** = hash of strategy@version, params, config hash, data
   hash, cost-model hash, risk config version and window. It excludes the
   creation time, so the same trial reproduces the same id.
5. **Data hash** covers file bytes *and* the timing policy, price kind,
   instrument and timeframe. Same bytes under a different `available_time`
   policy are a different experiment.
6. **Code version** is the git short hash with a `-dirty` suffix when the
   tree has uncommitted changes, or the literal `UNVERSIONED`. Never guessed.

## Consequences

- A PostgreSQL store needs only to implement `Journal.append/read_all` and the
  registry's `open/close/find`.
- Re-running an identical backtest increments the registry trial count. That
  is intended: it was a trial.
- Goldens in `tests/regression` pin simulation behaviour, not journal
  fingerprints, because fingerprints include the code version and would change
  on every commit.
