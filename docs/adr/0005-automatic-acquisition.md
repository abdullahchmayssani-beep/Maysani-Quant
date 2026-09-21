# ADR 0005 — Automatic Dukascopy acquisition: caching, retry, and CLI

- **Status:** Accepted
- **Date:** 2026-09-21

## Context

V0.2's real-data validation (ADR 0004) proved the pipeline against a
manually-downloaded Dukascopy website CSV export. That path is explicitly a
validation fixture, not an acquisition mechanism: it requires a human to
visit a website and download files by hand, one window at a time. The V0.2.1
objective is to complete `DukascopyProvider`'s `.bi5` path so it can acquire
data automatically - by instrument and bounded UTC window - whenever the
runtime has connectivity, with no browser or manual export involved.

Three gaps stood between the ADR 0003 `DukascopyProvider` and that goal:

1. It always re-fetched every hour over the network, even ones already
   verified on disk (ADR 0003 recorded this as an explicit limitation).
2. Any fetch failure (timeout, connection error, HTTP error) raised
   immediately, aborting the whole request - no retry, no way to acquire
   the rest of a window when one hour was unavailable, and no structured
   report of what happened.
3. There was no CLI entry point for "acquire this instrument for this
   window," only the config-driven `backtest`/`validate-data` path.

## Decision

### 1. A request-index in `RawArtifactStore`, separate from content addressing

Content addressing (`RawArtifactStore.put`/`get_bytes`, unchanged) answers
"do I have these exact bytes." It cannot answer "have I already fetched the
artifact for this (provider, instrument, window)" without fetching the
bytes first to compute their hash - fetching being exactly the expensive
step we want to skip. `RawArtifactStore` now also maintains a small pointer
index, `<root>/<provider>/<instrument>/_requests/<start>_<end>.json ->
{"sha256": ...}`, written by `put()` and read by the new
`find_by_request(provider, instrument, requested_start, requested_end)`.

`find_by_request` is self-healing: a missing index, a missing blob, or a
checksum mismatch is treated as a cache miss (fall back to fetching), never
as an error or a fabricated hit. This matters in practice - a partially
cleared cache directory must degrade to "fetch again," not crash.

### 2. Providers may declare themselves cache-aware; `MarketDataService` wires them up

`DukascopyProvider` gained an optional `raw_store` attribute. If a provider
exposes that attribute, `MarketDataService.__init__` sets it to the
service's own `RawArtifactStore` before running the pipeline - callers
construct a plain `DukascopyProvider(price_precision=...)` and never need to
separately wire a matching `raw_root`. `DukascopyCsvExportProvider` has no
such attribute and is completely unaffected (`hasattr` guards the wiring);
providers that don't do expensive I/O have no reason to opt in.

`DukascopyProvider.fetch_artifacts` checks `raw_store.find_by_request` for
every hour before touching the network; a hit yields a `RawArtifact`
reconstructed from the cached bytes with **no HTTP call at all**. Because
the reconstructed artifact carries the same content (hence the same SHA-256)
as the original fetch, re-running an identical acquisition reproduces the
identical `canonical_identity_hash` - retrieval time was already excluded
from that hash (ADR 0003 s.7) and remains so; caching changes performance,
never identity.

### 3. Per-hour outcomes: bounded retry, immediate non-retry for 4xx, never fatal to the whole window

FETCH is per-hour. Each hour's attempt ends in one of four states, recorded
in `DukascopyProvider.outcomes` (a plain list, this adapter's own reporting
surface - not part of the `MarketDataProvider` protocol, so no other
provider is affected):

| Status | Meaning | Retried? |
|---|---|---|
| `downloaded` | fetched (possibly after retries) | - |
| `cache_hit` | served from the raw cache, no network call | - |
| `missing` | a 4xx HTTP response | never - retrying "this does not exist" cannot help |
| `failed` | every attempt raised a transient/network error or 5xx | up to `max_attempts` total attempts, exponential backoff (`backoff_base_seconds * 2^(n-1)`, capped at `backoff_cap_seconds`) |

`missing`/`failed` hours are **skipped, not fabricated**: no synthetic tick
is invented for that hour, and the acquisition of the rest of the window
continues. Any resulting hole in the data surfaces exactly where every other
gap does - `SUSPICIOUS_GAP`/`WEEKEND_GAP` in `canonical_validate.py`,
unchanged from ADR 0003. `max_attempts` is a hard bound (`>= 1`, enforced in
the constructor): there is no code path that can retry unboundedly.

A hard failure remains possible and is not swallowed: PARSE-stage problems
(corrupt/malformed bytes that were successfully *downloaded*) still raise
`ArtifactParseError` through `require_parseable`, exactly as before this
ADR. Retry/skip logic lives entirely in FETCH and never masks a data
integrity problem in bytes that were actually retrieved.

### 4. Testability: injectable transport and clock, never mocking `urllib` internals

`DukascopyProvider` takes `opener: Callable[[str, float], bytes]` (default:
a one-line real `urllib.request.urlopen` wrapper) and `sleep_fn: Callable[[float],
None]` (default: `time.sleep`) as constructor arguments. Every acquisition
test in `tests/unit/test_dukascopy_acquisition.py` replaces both with
in-memory fakes - no test opens a socket or sleeps for a real second. The
one CLI-level test (`tests/unit/test_cli_acquire_dukascopy.py`) instead
patches `urllib.request.urlopen` directly, proving the exact code path a
real invocation uses without adding a CLI-specific seam.

### 5. `acquire-dukascopy` CLI command

`maysani-quant acquire-dukascopy --instrument EURUSD --start <UTC ISO> --end
<UTC ISO> [--timeframe H1] [--raw-root data/raw] [--canonical-root
data/cache/canonical] [--timeout-seconds 30] [--max-attempts 4]
[--backoff-base-seconds 1.0] [--no-require-bid-ask]` builds a
`DukascopyProvider` and a `MarketDataService` exactly as `backtest/runner.py`
does for `data.provider: dukascopy`, then prints requested window, artifacts
requested/downloaded/cache-hit/missing/failed (with per-hour detail for the
last two), raw artifact hashes, canonical identity, bar coverage, and
quality status. Exit code is non-zero if any bar failed validation or if the
run produced zero bars - the latter check exists so "the network is
completely unreachable" cannot look like a silent, trivially-successful
empty run.

### 6. `configs/v0_2.yaml`'s `data.dukascopy` block gained matching optional keys

`timeout_seconds`, `max_attempts`, `backoff_base_seconds` - all optional,
defaulting to the same values as the CLI, so a config-driven backtest run
against `data.provider: dukascopy` gets the same retry/timeout behavior as
the CLI path. `configs/v0_1.yaml` is untouched; these keys are only read
when `data.provider == "dukascopy"`.

## Consequences

- Re-running the same acquisition is safe, cheap, and deterministic: the
  second run is all cache hits, makes no network calls, and reproduces the
  identical canonical identity - proven in
  `test_repeat_acquisition_is_a_cache_hit_with_no_network_calls`.
- A future provider that wants the same caching behavior only needs to
  expose a `raw_store` attribute and consult `find_by_request` itself;
  nothing in `MarketDataService`, NORMALIZE, or CANONICAL VALIDATE changes.
- This session's sandbox still cannot reach `datafeed.dukascopy.com` (see
  `docs/STATUS.md`), so none of this has been exercised against a real
  socket. Every scenario in the table above (success, cache hit, retry,
  timeout, HTTP failure, corrupt artifact, missing hour, repeat run) is
  proven with injected fakes, not a live endpoint. The exact command to run
  against the real endpoint from a runtime with connectivity is recorded in
  `docs/STATUS.md`'s "External validation" section; running it requires no
  code change.
- Commercial redistribution/licensing status for Dukascopy data (Section 23)
  remains exactly as unresolved as before this ADR - acquisition mechanics
  and licensing are independent questions, and this ADR only addresses the
  former.

## Amendments from the V0.2 pre-freeze audit (2026-09-21)

The independent audit before the V0.2 freeze found four defects in the
mechanics this ADR describes. All are fixed and pinned by
`tests/unit/test_audit_regressions.py`:

1. **`pipeline_version` was recorded but not part of the identity.** ADR 0003
   s.7 listed the identity inputs; `pipeline_version` was written into the
   manifest and omitted from the hash, so a future NORMALIZE change would
   have let stale cache entries be served under an identity whose pipeline
   had moved on, and two materially different datasets would have collided
   on one hash. It is now an identity input. (This changed every existing
   canonical identity, which is correct and cost nothing - the only affected
   entry was a local, gitignored, regenerable cache.)
2. **The request index was keyed without `label`.** For an ADR 0004 window
   that yields both a `bid` and an `ask` artifact, the second `put` silently
   overwrote the first's pointer, so the window resolved to one side only.
   Latent (the CSV-export provider is not cache-aware) but a live landmine
   for any future multi-artifact cache-aware provider. The label is now part
   of the key; an empty label keys exactly as before.
3. **The raw manifest was only written on the branch that wrote the blob.** A
   blob whose sidecar went missing stayed permanently un-provenanced and
   permanently un-cacheable (every subsequent run re-fetched it). The sidecar
   is now written whenever it is absent, and never overwritten.
4. **Writes were not atomic.** An interrupted `write_bytes` left a truncated
   file under a name asserting the full content's hash, which `put` then
   correctly refused to overwrite - poisoning the cache until a human deleted
   it. All raw/canonical writes now go through `atomic_write_bytes`
   (temp file + `os.replace`), so a reader sees either the old file or the
   complete new one.
