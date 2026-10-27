# Findings and disposition

Date: 2026-10-27. Status: investigation executed; release acceptance failed.
No binaries vendored. No production Fortran source or Linux release changed.

These findings describe the initial bounded phase. The subsequently authorized
repair and math-runtime experiments now demonstrate paired-candidate parity;
see [the continuation outcome](package.md#authorized-continuation--2026-10-27)
for the 22-case and paired-control results and historical-reference limitations.

## Release and replay identity

261010 uses 7471bb5e981d14d0b8c1cdb88a16af305aed1b67; 261026 uses
b73e93b19a724d1991d341d38a18d11e742231bd. The latter's release sidecar documents
the late return-only SRC3 support and its restrictions. Both sidecars name the
remote-default branch wepp_260430_negmeltfix_comparator. The main source checkout
is a different, dirty branch; it was not used as the build source.

Linux: /usr/bin/gfortran 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1).
Windows: native WinLibs GNU Fortran 13.3.0, x86_64-ucrt-posix-seh, r1, on blarhg.
Windows execution used C:/Users/roger/miniconda3/python.exe and PE executables;
WSL and IFX were not used. The existing checksum-recorded 261010 Windows candidate
was reused for baseline replay; diagnostics and experimental candidates were
freshly built. The 261026 baseline was freshly built on both platforms.

Inputs are the earlier campaign's committed-source single-daily control (four
years, one OFE) and watch-p24 (45 years, 14 OFEs), including shared context.
Their source is d354e3c998f81955f9d9e5ca7d01ca56e1a9f04b. Retained input hashes,
source archive hashes, binary identities and execution receipts are in artifacts/.
Reference replays use unchanged released Linux binaries. Complete generated
outputs remain under /tmp/native-parity-20261027 and the corresponding Windows
C:/tmp/native-parity-20261027; these temporary trees are not durable storage.
The durable package retains diagnostics, comparisons, scripts and patches.

## Reproduced baseline

Both releases complete both native Windows cases, but fail numerical acceptance.
The small control passes the water/erosion file thresholds while failing the
all-output/event-duration check. Watch-p24 fails water, erosion and all-output
checks. Runtime completion is not evidence of scientific validity.
The rebuilt 261026 Linux control and watchlist case pass comparison to the
released Linux executable. Comparison thresholds remain water 1%, erosion 10%,
all-output diagnostics 1%, with absolute floor 1e-9 and structural checks.

## Cause isolated for the snowmelt-duration discrepancy

Opt-in instrumentation captures float32 bit patterns on days 50–53. This window
is deliberately bounded; it is not an exhaustive first-difference trace of all
state throughout the simulation. Radiation inputs agree bit-for-bit within this
window. At day 52, hour 9, radcur returns 0x3FD6F2A3 on Linux and 0x3FD6F2A9 on
Windows. The same difference reproduces in a standalone copy of radcur with
identical arguments and -O2 -ffp-contract=off.

For the angle 0xBF3766DD, the probe's sine result is 0xBF281C71 on Linux versus
0xBF281C70 on Windows: one float32 ULP. We do not infer which runtime is more
accurate from this experiment. Radiation differences propagate to snow depletion.
Windows retains 1.1641532182693481e-10 m of snow depth at hour 10, followed by
4.0745368884431699e-11 m melt at hour 11; Linux has zero. In disag.for the test
hrmlt > 0 counts this residual as a whole additional melt hour. The resulting
one-hour event-duration change alters peak runoff by about 9.1%.

This is a demonstrated amplification path in the small control. It does not
explain all watchlist differences. Observation-only outputs retain the control's
baseline acceptance behavior; no physical threshold was changed.

## Proven bounds defects

Checked builds use -fcheck=all with the same optimization and initialization
profile, plus warnings and implicit-interface diagnostics.

1. Both releases, both platforms: pmetcoef.for:72 writes kcb(7) when the array
   has length six. Watch-p24 supplies 14 crop definitions. ccrpet.inc sizes kcb
   and rawp using mxcrop=6, while input iterates over ncrop. This is an actual
   checked runtime failure, not just a compiler warning.
2. An isolated 261026 lane sizes these two arrays by ntype, consistently in both
   COMMON users, and adds the missing pntype include to pmetcoef. On both
   platforms this passes the first failure but reaches contin.for:1094 at year
   31: ui_epht has a first dimension of only 30. The complete case has 45 years;
   shared wepp_ui.txt enables this accumulation path. ui_esht and ui_sepht share
   the same declared year limit. The checked execution establishes the first
   failing access, not every downstream consequence of unchecked execution.

The crop patch remains experimental. We have not established how much of the
watchlist platform discrepancy comes from these defects. The full configured
checked replay did not pass, so no corrected model or release is claimed.

## Bounded trigonometry lane

A second independent lane changes only radcur's sine/cosine evaluation to double
precision followed by conversion back to real. It does not combine the crop
patch or alter thresholds. It was built and replayed on both platforms for both
releases.

For each release's small control, six of seven output files become text-identical
across platforms after newline normalization, including event, element and pass
files. The remaining water file has small differences. However, the Linux lane
now differs from the original Linux release by the same one-hour event-duration
change; the existing-release all-output gate fails. Watch-p24 still fails native
Windows acceptance. Therefore the patch is not promoted. Agreement on one
control is insufficient, and changing the Linux reference would require a new
scientifically validated release rather than relabeling these versions.

## Full-capacity watershed

A fresh unmodified 261026 native Windows watershed build reaches the linker and
fails with non-representable symbol addresses. The Linux executable contains
14,057,566,448 bytes of BSS. This confirms the earlier capacity finding for the
new release. No dimensions were reduced and no storage-layout port was attempted
because the numerical acceptance gate remains open.

## Validation and closure boundary

34 recorded model executions comprise 28 completions and six checked bounds
failures. Windows input verification found zero mismatches against the Linux
input manifest. The comparator's own regression suite passed: three tests. Runtime receipts and
numerical reports are retained separately. Initial broad observation on Windows
was stopped because per-record file logging was too costly; fresh uninstrumented
replays and the bounded trace replaced it. Early archive/setup attempts were
corrected before recorded builds; archives include only required source/tool
paths and the 261026 calendar module. No partial setup is counted as a pass.

Full upstream release pytest/watchlist, paired watershed replay and downstream
vendoring gates were not run: native release prerequisites failed. The prior
22-case campaign remains historical evidence, not a new 22-case acceptance run.
This campaign's exact scope is two cases per release, with diagnostic and causal
lanes as recorded. No assertion of WSL parity was retested here.

The bounded investigation is complete; release readiness is not. Continuation
requires a source-correctness package for the crop and UI year bounds, then a
scientifically reviewed snow-exhaustion/event-support policy or deliberately
matched math implementation. Revalidate Linux behavior and both platform suites
before undertaking the full-capacity COMMON-storage port. No arbitrary epsilon,
tolerance relaxation, capacity reduction or broad math replacement is accepted
by this package.
