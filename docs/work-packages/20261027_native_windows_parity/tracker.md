# Tracker

## Final authorized disposition — 261027

Closed successfully on 2026-10-27. The revised scope releases only native Windows
261027. Both binaries are vendored; all 214 small-suite and 3,443 medium-run
output files match the new Linux baseline after CRLF normalization. The complete
medium case has 491 hillslopes, 211 channels and nine years. The proposed old
release backports are canceled. See [release validation](../../windows-release-261027.md).
Earlier investigation dispositions below are retained as history.


The checklist below covers the initial bounded investigation. The authorized
continuation now passes 22/22 hillslope and 10/10 paired-control cross-platform
comparisons using a shared experimental math runtime. Historical Linux behavior
changes, release integration, 261010 backport and vendoring remain open. See
[the continuation outcome](package.md#authorized-continuation--2026-10-27).

- [x] Read previous build/research evidence; verify blarhg is reachable.
- [x] Identify release commits: 261010 7471bb5e981d14d0b8c1cdb88a16af305aed1b67;
  261026 b73e93b19a724d1991d341d38a18d11e742231bd.
- [x] Freeze provenance and reproduce baseline.
- [x] Run diagnostic and observation lanes.
- [x] Disposition bounded causal experiments and release feasibility.
- [x] Validate tooling/docs and close investigation with explicit vendoring status.

## Disposition

Closed 2026-10-27 as an executed bounded investigation, not as release-ready.
Baseline numerical gates fail for both versions. Opt-in traces and a standalone
radcur probe identify a float32 sine discrepancy and its event-duration effect.
Checked builds find the six-crop coefficient bound; an isolated correction then
finds the 30-year UI accumulation bound on both platforms. A separate radcur
precision lane aligns control event outputs but changes the original Linux
reference and leaves watchlist acceptance failing. Fresh 261026 watershed link
fails at full capacity. No patch promoted and no binary vendored.

Comparator regression tests: three passed. Package documentation lint: five files,
zero errors/warnings using markdown-doc directly. wctl resolves the wepppy root
and cannot scope this sibling repository correctly; its incidental root-wide
lint findings are unrelated and were not changed. Spelling preview is clean.
Source and input provenance, 34 execution receipts, comparison gates, patches,
compiler logs and continuation requirements are retained in artifacts/ and
findings.md. Full release regression gates are deferred until prerequisites pass.
