# data/

V0.1 ships **no market data**. Vendor data is licensed and is excluded by
`.gitignore`; the only CSVs that may be committed are `SYNTHETIC_*` fixtures.

## Synthetic fixture

```bash
maysani-quant make-synthetic-dataset --out data/SYNTHETIC_eurusd_d1.csv
```

Deterministic (fixed LCG seed), byte-identical on every machine, 600 daily
bars. The filename must contain `SYNTHETIC` or the command refuses to write.
Bars loaded from such a file carry `QualityFlag.SYNTHETIC`, and reports open
with a banner. **Numbers measured on it describe the generator, not EUR/USD.**

## Supplying real EUR/USD data

Point `data.path` in `configs/v0_1.yaml` at your file, or pass
`--dataset path/to/file.csv`. Then run `maysani-quant validate-data` before any
backtest — the backtest refuses to run on data that fails validation.

### Required columns

| Column | Meaning |
|---|---|
| `timestamp` | bar **start** time, ISO-8601. Naive times are read as UTC |
| `open`, `high`, `low`, `close` | prices |

### Optional columns

| Column | Effect |
|---|---|
| `end_time` | bar end; otherwise `timestamp + timeframe` |
| `available_time` | when the row could first be known. Overrides the config policy |
| `bid_close`, `ask_close` | true executable quotes; `spread` is derived from them |
| `spread` | per-bar spread, used when `costs.spread_model: dataset` |
| `volume` | recorded, not used by V0.1 logic |

### Timing policy

If the file has no `available_time` column, the config decides:

- `bar_close` — the bar is known at its close (default)
- `bar_close_plus_lag` — known `available_time_lag_seconds` after close

The policy is part of the `data_hash`. The same bytes under a different policy
are a different experiment.

### Midpoint vs bid/ask

With `price_kind: midpoint`, the engine does **not** treat the price as
executable. The configured spread scenario is applied to every fill, and the
report prints it under "cost model assumptions (configured, not observed)".
With true bid/ask data, set `costs.spread_model: dataset`; the loader then
fails loudly on any bar missing a spread rather than falling back.

## Open questions this directory depends on (Section 23)

- Which provider supplies EUR/USD with adequate bid/ask fidelity, and under
  what licence and redistribution terms?
- Daily, hourly, or both? Start with the horizon that can be simulated
  honestly with the data actually available.

## V0.2: provider-independent pipeline (see `docs/adr/0003`)

Two new local, gitignored directories hold everything the Dukascopy provider
(or any future provider) produces. Neither is committed to git - see
`.gitignore`.

- `data/raw/<provider>/<instrument>/<sha256[:2]>/<sha256>.bin` — the
  provider's original artifact bytes, verbatim, plus a `.manifest.json`
  sidecar (SHA-256, provider/version, requested window, retrieval time).
  Content-addressed: identical bytes are never rewritten.
- `data/cache/canonical/<provider>/<instrument>/<canonical_identity_hash>.csv`
  — validated, normalized `MarketBar`s, plus a `.manifest.json` recording the
  reproducible identity (raw hashes + provider + instrument + window +
  schema/policy version - retrieval time is provenance, not part of the
  identity).

Set `data.provider: dukascopy` in a config (see `configs/v0_2.yaml`) to use
this path instead of a CSV file; `data.provider: csv` (or omitting the key)
is exactly V0.1's behaviour, unchanged.

**As of this commit, no real Dukascopy artifact has been fetched in this
repository.** This session's network egress policy denies
`datafeed.dukascopy.com`; the pipeline is built and tested entirely against
offline fixture bytes (see `tests/unit/test_dukascopy_adapter.py` and
`tests/unit/test_market_data_service.py`). Numbers produced by
`configs/v0_2.yaml` will not exist until that access is available and the
pipeline has actually been run against it.
