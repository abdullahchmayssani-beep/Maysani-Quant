# ADR 0004 — PARSE operates on artifact groups, not single artifacts

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

ADR 0003 defined `MarketDataProvider.parse_artifact(artifact: RawArtifact) ->
Iterator[ProviderTick]`: one artifact in, ticks out. That fit Dukascopy's
`.bi5` feed, where a single hourly file already carries both bid and ask.

The first real-data validation sample is a Dukascopy **website CSV export**
(`EUR-USD_1Tick_{BID,ASK}_2026-09-17_12_00-12_00_Etc_UTC.csv`), not a `.bi5`
file. The export tool hands back **two separate files** for one requested
window - a BID-only stream and an ASK-only stream - each row carrying one
side's price (`Open=High=Low=Close` for that tick) and a volume. Neither
file alone contains a paired quote; a single `RawArtifact` is no longer
sufficient input to produce one `ProviderTick`.

## Decision

`parse_artifact(single)` becomes `parse_artifacts(group: Sequence[RawArtifact])`.
`MarketDataService` groups the flat stream `fetch_artifacts` yields by
identical `(requested_start, requested_end)` before calling PARSE - a
Dukascopy `.bi5` hour is naturally a group of one (each hour has a unique
window); the CSV export's BID and ASK artifacts share the same declared
window and land in one group of two. `RawArtifact` gains an optional `label`
field (e.g. `"bid"` / `"ask"`) purely as provenance/PARSE-time metadata; it
plays no role in content addressing.

This is the smallest change that keeps the rest of ADR 0003 intact:

- FETCH still yields a flat `Iterator[RawArtifact]`; RAW STORE still stores
  each artifact independently and immutably, by its own content hash - no
  change there.
- NORMALIZE, CANONICAL VALIDATE, CANONICAL STORE, and everything downstream
  of `MarketDataService` are **completely unchanged**. They only ever see
  `ProviderTick`s or `MarketBar`s.
- A future provider that genuinely needs several jointly-produced artifacts
  (e.g. a feed that splits by field across files) fits the same mechanism;
  a provider that doesn't (like `.bi5`) pays for it with one trivial
  `for artifact in group:` wrapper around its existing single-artifact logic.

### Row-pairing policy for the CSV export (documented, verified against the
real sample, not against Dukascopy's own docs - see ADR 0003's precedent on
`[UNVERIFIED]` claims)

The BID and ASK files are paired **by row index**, not by re-deriving a join
from timestamps, because:

1. Both files have the identical row count.
2. Every row's timestamp matches its counterpart in the other file, at every
   index, in the real sample (5293/5293 rows).
3. Pairing by index produces `ask >= bid` at every one of those 5293 rows,
   across an hour where the price moved roughly 180 pips - a coincidence
   this consistent is implausible under a wrong pairing.
4. The resulting spread distribution (mostly 1-4 pips, EUR/USD-typical) is
   further corroborating evidence, not proof.

`DukascopyCsvExportProvider.parse_artifacts` **verifies** (2) before pairing
- equal row counts and identical row-by-row timestamps - and raises
`ArtifactParseError` if either check fails, rather than silently falling
back to a timestamp-based join that could mispair ambiguous same-second
ticks. This turns "we assume row alignment" into "we require and check row
alignment," consistent with CLAUDE.md's rule against silently assuming a
gap-filling policy.

The 1-second timestamp resolution (versus `.bi5`'s millisecond resolution)
is a genuine fidelity limitation of this ingestion path, not a bug; it is
recorded in the adapter's provenance (`provider_version` /
docstring) and does not affect NORMALIZE's H1/M1-scale bar aggregation, but
would matter for any future tick-level use.

## Consequences

- `DukascopyProvider` (`.bi5`) needed a one-line signature change
  (`parse_artifact` -> `parse_artifacts`, body wrapped in a `for artifact in
  group:` loop over what is always a singleton group in practice).
- `MarketDataService._run_pipeline` groups artifacts before parsing; raw
  storage and validation are unaffected (still per-artifact).
- `DukascopyCsvExportProvider` (`data/providers/dukascopy_csv_export.py`) is
  the only module that knows the website export's column layout and the
  row-pairing policy above.
- The real uploaded CSVs are never committed to git (see `.gitignore`'s
  existing `data/raw/` / `data/cache/` rules); only hand-built, clearly-fake
  fixture text exercises this adapter in the committed test suite.
