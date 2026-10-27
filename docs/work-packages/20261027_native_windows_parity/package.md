# Native Windows GNU Fortran parity

## Final authorized disposition — 261027

Closed successfully on 2026-10-27. The revised scope releases only native Windows
261027. Both binaries are vendored; all 214 small-suite and 3,443 medium-run
output files match the new Linux baseline after CRLF normalization. The complete
medium case has 491 hillslopes, 211 channels and nine years. The proposed old
release backports are canceled. See [release validation](../../windows-release-261027.md).
Earlier investigation dispositions below are retained as history.


Status: closed as a bounded investigation, 2026-10-27. Owner: Roger.
Release acceptance: failed; no binaries vendored.

## Objective

Execute the bounded numerical investigation proposed in windows-releases-20261026.md
for wepp_261010 and wepp_261026 (including the late dry-day soil-return fix).
Use native Windows blarhg and GNU Fortran 13.3 on both platforms. IFX and WSL
are excluded as delivery mechanisms. Preserve released Linux references and
existing working-tree edits. This is causal investigation, not a physics rewrite.

## Scope and sequence

1. Freeze release provenance and identical inputs in isolated source snapshots.
2. Reproduce single-daily and watch-p24 using the released Linux binaries and
   native Windows candidates. Check runtime success separately from parity.
3. Run bounds/runtime diagnostics on both platforms; enable observation and
   capture the earliest differing state/branch before behavioral experiments.
4. Test bounded, single-variable compiler or localized portability lanes only
   when supported by evidence. Compare Linux lanes to the Linux releases too.
5. If numerical agreement is tractable, assess full-capacity Windows storage.
   Otherwise close the investigation with a precise continuation boundary.

## Acceptance and stop conditions

Retain the existing water 1%, erosion 10%, absolute floor 1e-9 gates, structural
checks and event timing/peak evidence; do not relax tolerances after failures.
No capacity reduction, broad math-library replacement, threshold tuning, formula
changes or silent alteration of released Linux artifacts. Stop and scope further
work if these are required. Initial scope is a bounded causal campaign, not a
promise of successful release. Full-capacity watershed remains a separate known
PE image-size blocker. Vendor only after both profiles build and full paired
release gates pass; unsuccessful candidates remain outside bin/.

## Deliverables

Reproducible commands/scripts, source and binary hashes, diagnostic logs,
comparison and causal findings, tracker and final disposition. Source edits in
experimental snapshots are retained as patches, not promoted without validation.

## Outcome

See [findings](findings.md), [reproduction](reproduce.md) and retained artifacts.
34 recorded model executions: 28 completed, six stopped on checked bounds errors.
The standalone radiation probe isolates a platform math difference amplified by
strict positive-melt duration counting. Two concrete array-bound defects and the
fresh 261026 watershed link failure prevent release acceptance. Experimental
patches remain isolated; production source, Linux references and bin/ are unchanged.
The investigation is complete; native release parity and vendoring remain open.

## Authorized continuation — 2026-10-27

Roger subsequently authorized bounds repairs, reduced Windows capacity and a
shared deterministic sine implementation within 1e-4 of the current function.
The follow-up source incident is
`wepp-forest-release-20261009/docs/ablation/20261027-native-portability` on the
canonical default-branch worktree. It repairs the crop bounds, removes unread
30-year UI accumulators, implements the shared radiation trigonometry kernel,
and adds a 4500-hillslope/1500-channel Windows profile. The first investigation's
stop conditions above describe its original scope, not this later authorization.

The follow-up kernel is bit-identical across 151,109 sampled angles on both
platforms, with maximum intrinsic difference 5.96e-8. All 536 source tests,
22 checked hillslope cases per platform and 32 ordinary paired/native executions
per platform pass runtime checks. Whole-model strict comparison remains open;
no dated release binary has been replaced or vendored. See the source incident
for exact residuals and the rejected broader trigonometry-dispatch experiment.

The subsequent native math-runtime campaign now passes all-output, water and
erosion comparisons for 22/22 hillslope cases and 10/10 paired physical controls.
The full 100-year p40 water record matches numerically. A 145,937-evaluation math
probe has zero cross-platform bit differences, with at most one float32 ULP
change from native functions on the sampled arguments. Sunmap acos evaluation
accounts for the dominant long-run p40 divergence; broader shared float math
dispatch closes the observed residual.

This establishes parity between corrected candidates, not unchanged historical
Linux releases. The new Linux candidate passes only 12/22 water and 20/22 erosion
comparisons against the preceding corrected Linux candidate. The experimental
runtime is retained for scientific review and release integration; 261010 has
not been backported and no dated binary is vendored. Detailed evidence is in
`wepp-forest-release-20261009/docs/ablation/20261027-native-portability/campaign-continuation.md`
and its `artifacts/campaign/` directory. The earlier stop conditions and failed
comparisons above remain historical records of the original bounded phase.
