# Windows releases 261010 and 261021

## Build and validation plan

Build native Windows watershed and hillslope executables on blarhg from the
source commits recorded in the corresponding Linux release metadata. Use isolated
source snapshots and retain compiler commands, hashes, and comparison results.
Vendor explicitly versioned executables only after successful Windows execution
and numerical comparison with the matching Linux release. Keep the existing
bootstrap default executable until a separate default-selection change is made.

- 261010: `7471bb5e981d14d0b8c1cdb88a16af305aed1b67`.
- 261021 revision 2: `d354e3c998f81955f9d9e5ca7d01ca56e1a9f04b`.
- Source lineage: `wepp_260430_negmeltfix_comparator`.
- Linux references: `/workdir/wepppy/wepp_runner/bin/wepp_<tag>` and `_hill`.

## Progress

- Verified source commits against Linux sidecars; both source objects available.
- Existing Linux and Windows source checkouts contain unrelated changes; isolated
  snapshots will preserve them.
- Native MSYS2 UCRT64 and MinGW64 GNU Fortran 16.1.0 are available on blarhg.
- Hillslope candidates built with GNU 16.1 and GNU 13.3; Windows system runtime
  dependencies inspected. Linux reference replay and Windows candidate execution
  records are retained below.
- Blocked before vendoring: full-capacity watershed PE link failure, pending
  capacity selection, and failed numerical parity. No release binaries have been
  added to `bin/` and the bootstrap default remains unchanged.

## Findings

- Linux reference SHA-256 values match their release sidecars. All 32 fresh
  executions per release passed (ten hillslope/watershed pairs and twelve
  permanent hillslope watchlist cases).
- Full Linux watershed capacities fail native PE linking on blarhg with
  non-representable symbols beyond the image address range. A proposed Windows
  capacity of 4,500 hillslopes / 1,500 channels awaits operator selection.
- GNU Fortran 16.1.0's default dialect rejects legacy missing commas in output
  FORMAT descriptors; its runtime error path then crashes. GDB identified
  `outfil.for:208` and `Missing comma between descriptors`. `-std=legacy` fixes
  the first native hillslope replay without source changes. Increasing stack
  size alone did not fix this and is not part of the chosen build profile.

- A checksum-verified, isolated [WinLibs GNU Fortran 13.3.0 toolchain](https://github.com/brechtsanders/winlibs_mingw/releases/tag/13.3.0posix-11.0.1-ucrt-r1)
  was also tested to match Linux's compiler version. Archive SHA-256:
  `6c90485da4d9966683a83a1e5f3a0b1084d2a5ba2e57e8b27c0634afe3983776`.
  It reproduces the same preliminary snowmelt-duration difference as GNU 16.1.
- In the `261010` single-OFE daily control, Windows produces an 11-hour runoff
  event versus Linux's 10 hours on February 21 in simulation years 2–4. Peak
  runoff changes from 2.731 to 2.482 mm/h (about 9.1%). Daily water output differs
  by at most 0.00001 in the preliminary case. Thus successful execution does not
  establish numerical parity, and compiler-version matching alone is insufficient.
- The 121-year 1980–2100 Gregorian control completed using the `261021` Windows
  hillslope binary and both Linux reference binaries.

## Replay and evidence locations

- Linux source snapshots: `/tmp/wepp-windows-<tag>-20261026`.
- Linux fresh outputs: `/tmp/wepp-parity-linux-<tag>`.
- Windows GNU 16.1 builds: `C:\tmp\wepp-windows-<tag>-20261026`.
- Windows GNU 13.3 builds: `C:\tmp\wepp-windows-<tag>-gcc133-20261026`.
- Windows fresh hillslope replays: `C:\tmp\wepp-parity-win-hill-legacy-<tag>`
  (GNU 16.1) and `C:\tmp\wepp-parity-win-hill-gcc133-<tag>` (GNU 13.3).
- Source inputs: `d354e3c`'s committed `tests/fixtures/physical_water` and
  `tools/physical_water_case.py` (five layouts, daily/hourly, four years), plus
  the twelve committed cases in `docs/ablation/hillslope_watchlist.csv`.
- Runner: `tools/run_windows_release_cases.py`. All runs require zero exit status,
  the appropriate success marker, and absence of recognized runtime errors.

## Compiler profile

Both native toolchains use the source Makefile with these explicit flags:

```text
FFLAGS=-c -fno-align-commons -mcmodel=medium -g -fbacktrace -O2 -ffixed-form -ffixed-line-length-72 -ffpe-trap=invalid,zero,overflow -finit-local-zero -std=legacy
FFLAGS_F90=-c -fno-align-commons -mcmodel=medium -g -fbacktrace -O2 -ffpe-trap=invalid,zero,overflow -finit-local-zero -std=legacy
LDFLAGS=-mcmodel=medium -static
```

PE imports contain only Windows system/UCRT DLLs; no separately installed
GNU Fortran runtime is needed. Binaries are invoked by native Windows Python,
not WSL. Source physics and capacity files remain unmodified.

## Validation outcome

Runtime success and numerical parity are separate checks. Both releases completed all 22 Windows hillslope cases under each compiler
(GNU 16.1 and GNU 13.3): 88 successful native executions total. Each Linux reference
completed 32 executions, including ten paired watershed replays. The Windows
watershed candidates cannot yet be linked at Linux capacity, so Windows
watershed parity is untested.

GNU 16.1 comparisons use the source repository's raw comparator at `d354e3c`.
All-output diagnostics use 1% relative tolerance; domain lanes use the existing
1% water / 10% erosion thresholds with the existing 1e-9 absolute floor.
Water files are `*.wat.dat`; erosion files are `*.ebe.dat` and `*.loss.dat`.
Physical-control all-output checks cover `H1.*`; watchlist checks cover every
output file. File-set, row-count and numeric-field-count differences also fail.
CRLF versus LF does not count as a numerical difference.

For 261010, 6/22 all-output checks, 12/22 water checks, and 17/22 erosion checks
pass. For 261021, the corresponding counts are 6/22, 12/22, and 17/22.
For example, the p24 water output has 63,172 values above tolerance, with
a maximum absolute difference of 98.29 across its columns; its event output also
has a structural mismatch. These are not merely executable hashes or line-ending
differences. Both GNU 13.3 release candidates reproduce the single-daily control
peak-flow/duration failure; complete GNU 13.3 numerical comparison is not claimed.

Retained machine-readable evidence lives in [windows-releases-20261026](windows-releases-20261026/).
`candidate-builds.json` records source, compiler and binary hashes; execution JSON
files record individual runs. The comparison reports distinguish runtime success
from failed numerical acceptance. The full raw output trees remain in the
Linux and Windows temporary directories listed above.

## Remaining work

1. Select an acceptable native Windows watershed capacity. The proposed
   4,500-hillslope / 1,500-channel configuration changes supported project size,
   so it has not been applied while the operator's choice is pending.
2. Isolate the cross-platform numerical divergence without silently altering
   the released physics or relaxing acceptance tolerances.
3. Rebuild and rerun the full paired hillslope/watershed validation before
   vendoring either release. Upstream full pytest/release gates have not been
   rerun for a release because the Windows build/parity prerequisites failed.

## Native GNU Fortran feasibility research

Research date: October 26, 2026. IFX and WSL are excluded from the proposed native
path. This assessment does not authorize a capacity reduction or claim a release
has passed numerical validation.

### Assessment

Native GNU Fortran distribution is feasible. Packaging is already demonstrated
by successful Windows executions with only Windows system/UCRT DLL imports.
Full watershed capacity needs a storage-layout port; numerical agreement needs a
bounded causal investigation. Neither issue is inherent to fixed-form syntax.
Exact reproduction of existing Linux releases is a harder requirement than
scientifically acceptable agreement for a newly validated cross-platform release.

### Fixed-form build practices

- Preserve source bytes, include dimensions, and compiler/runtime provenance.
  Use `-ffixed-form -ffixed-line-length-72` for fixed-form units, retaining free
  form for `.f90` units. Changing the line limit can activate previously ignored
  source. `-std=legacy` is needed for these FORMAT descriptors, but also permits
  argument mismatches; it is compatibility handling, not proof of correctness.
  [GNU Fortran dialect options](https://gcc.gnu.org/onlinedocs/gcc-13.3.0/gfortran/Fortran-Dialect-Options.html)
- Keep COMMON declarations, kinds, alignment, and storage lifetime consistent in
  every compilation unit. Preserve existing `-fno-align-commons` and initialization
  behavior. Do not try blanket default-real promotion or `-fno-automatic` as a
  numerical fix. `-frecursive` does not relocate COMMON storage to a heap.
  Allocatable arrays require deliberate initialization; `-finit-local-zero` does
  not initialize them and also suppresses affected uninitialized-variable warnings.
  [GNU Fortran code generation](https://gcc.gnu.org/onlinedocs/gcc-13.3.0/gfortran/Code-Gen-Options.html)
- Maintain a separate diagnostic build with bounds/runtime checks, backtraces,
  and interface warnings. Compile the main program with the checks too. Missing
  interfaces need investigation; suppressing warnings is not an ABI repair.
  [GNU Fortran warnings](https://gcc.gnu.org/onlinedocs/gcc-13.3.0/gfortran/Error-and-Warning-Options.html),
  [argument conventions](https://gcc.gnu.org/onlinedocs/gcc-13.3.0/gfortran/Argument-passing-conventions.html)
- Pin the full GNU toolchain and CRT, not just the compiler version. UCRT64 is
  MSYS2's recommended general choice. Do not mix UCRT and MSVCRT object/static
  libraries. End users need the runtime dependencies, not the MSYS2 build tools.
  [MSYS2 environments](https://www.msys2.org/docs/environments/)
- Avoid fast-math and host-specific instruction selection during comparison.
  Compare explicit CPU targets, floating-point contraction settings, and scalar
  versus vector builds. GCC enables vectorization at `-O2`; GNU 13.3 defaults to
  allowing contraction. These settings can narrow a cause, but cannot guarantee
  equal math-library results.
  [GCC optimization options](https://gcc.gnu.org/onlinedocs/gcc-13.3.0/gcc/Optimize-Options.html),
  [GCC 12 vectorization change](https://gcc.gnu.org/gcc-12/changes.html)

A local compile probe confirmed that GNU Fortran 13.3 rejects
`-fexcess-precision=standard` as unimplemented for Fortran. It should not be copied
from C/C++ reproducibility advice into this build.

### Full capacity: concentrated static-storage problem

`size` reports 14,057,566,448 bytes (13.09 GiB) of BSS in `wepp_261021`, versus
2,553,676 bytes in its hillslope executable. BSS is static address-space storage,
not a measurement of resident RAM. Microsoft documents a 2 GB PE32+ image limit;
that is separate from the much larger address space available to a 64-bit process.
[PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format),
[Windows memory limits](https://learn.microsoft.com/en-us/windows/win32/memory/memory-limits-for-windows-releases)

The five largest COMMON blocks are:

| Block | GiB | Declaration |
| --- | ---: | --- |
| `inpman1` | 5.869 | `cinpman1.inc` |
| `rinpt1a` | 1.678 | `crinpt1a.inc` |
| `inpman2` | 1.677 | `cinpman2.inc` |
| `yield` | 1.676 | `cyield.inc` |
| `cdrain` | 0.839 | `ccdrain.inc` |

Moving these five blocks out of static storage would leave approximately 1.35 GiB
of BSS, before new descriptors/runtime changes. An include-reference inventory
finds 27 source units affected directly or transitively. Several large arrays are
products of two 15,000-element dimensions. This is evidence for a focused module/
allocatable-array port, not a need to rewrite every Fortran routine.

This remains a design hypothesis, not a validated patch. Preserve shapes, kinds,
column-major indexing, initial values, persistence, and all callers; audit aliases
and initialization loops. Moving storage must not change formulas. Test the same
port on Linux against the existing release first, then Windows. Measure memory
commit, startup cost and repeated-run behavior. Merely adding stack/linker flags
cannot solve this COMMON-block image-size problem. A reduced-capacity build is
an alternative, not the only no-WSL option.

### Numerical agreement: demonstrated differences, unresolved cause

The Linux binary imports scalar glibc math functions and vector `sinf`, `logf`,
and `powf` entry points. Disassembly places the vector calls in `tmpfun`, `seddia`,
and `impmai`. Native Windows uses a different runtime. GNU libc does not promise
correct rounding for most transcendental functions, so matching compiler versions
is insufficient to guarantee identical results.
[GNU libc math accuracy](https://sourceware.org/glibc/manual/latest/html_node/Errors-in-Math-Functions.html)

A bounded experiment rebuilt the unchanged `261010` hillslope source with local
GNU 13.3. All seven single-daily output files matched the released Linux reference
exactly. Recompiling only `tmpfun` without loop/SLP vectorization removed its vector
`sinf` dependency, but all seven outputs remained identical to the Linux control.
The Windows peak-flow/duration difference remained. Thus this particular vector
call does not explain that control's discrepancy; scalar math, other code paths,
ABI/initialization defects, and amplified branch differences remain hypotheses.
No formula, tolerance, or release binary was changed.

File-pass counts alone are inadequate scientific acceptance metrics. A fresh
column-aware check of GNU 16.1 Windows versus Linux, using aligned dates and equal
areas for the terminal OFE, found:

| Case | Quantity | Cumulative relative difference | Additional context |
| --- | --- | ---: | --- |
| p24, 45 years | Reported QOFE runoff depth | -0.0278% | Largest daily difference 31.82 mm |
| p24, 45 years | Transpiration | +11.93% | +227.43 mm over the period, about 5.05 mm/year |
| p49, 100 years | Reported QOFE runoff depth | +0.00202% | Largest daily difference 1.90 mm |
| p49, 100 years | Soil evaporation | -16.99% | -45.53 mm over the period, about -0.46 mm/year |

These are sums of a particular reported depth for one OFE, not watershed closure
or sums of mixed-unit columns. They show why acceptance needs absolute magnitude,
cumulative behavior, daily timing and peaks as separate measures. Do not loosen
thresholds after seeing a failure, or assume all discrepancies are negligible.

### Bounded next investigation and stop conditions

Recommended initial engineering timebox: two working days, not a promise that a
release can be completed in that time.

1. Preserve the current Linux references and output contracts. Use single-daily
   and one failing watchlist seed as small discriminating cases.
2. Run diagnostic builds on both platforms to check bounds, interfaces, storage
   lifetime and floating-point environment. Fix demonstrated undefined behavior
   before comparing optimization switches.
3. Capture the first differing state/branch with full-precision or bit-pattern
   telemetry. Only then test one change at a time: contraction, vectorization,
   optimization level, or the particular math function involved. Compare each
   Linux diagnostic build to the original release as well as to Windows.
4. Identify a bounded cause and rerun the affected cases. If agreement requires
   broad replacement of math routines, repeated branch-threshold changes, or
   relaxed tolerances, stop and scope a larger numerical-port project.
5. Proceed with the five-block storage port only when the numerical path looks
   tractable, unless a standalone capacity-port experiment is explicitly selected.

Rough planning ranges, based on the inventory rather than an implemented port:

- Build/package reproducibility: low risk, hours to a few days.
- Five-block storage port with focused validation: medium risk, several days to
  a few weeks, depending on aliasing, initialization and regression findings.
- Numerical parity: uncertain; a localized cause could be a few days, while
  matching existing glibc-dependent event behavior can become a multi-week effort.
- Exact cross-platform reproduction of every existing Linux output: high risk;
  no finite completion estimate is justified by the current evidence.

### Other no-WSL routes

- **Cygwin:** requires a source rebuild and a compatibility DLL. It does not run
  existing Linux binaries, supply glibc automatically, or eliminate the native
  image/storage issue. It adds another runtime to validate, so it is not the
  first investigation choice here. [Cygwin](https://cygwin.com/)
- **Bundled Linux VM:** can retain the Linux binaries and user-space libraries,
  shifting the work toward packaging, file transfer and runtime maintenance.
  QEMU's accelerated Windows backend requires the Windows Hypervisor Platform
  feature. Software emulation is another option, but performance needs measurement
  before considering it for WEPP. This avoids WSL specifically, not the need for
  a Linux execution environment. [QEMU WHPX](https://www.qemu.org/docs/master/system/whpx.html),
  [QEMU emulation](https://www.qemu.org/docs/master/about/emulation.html)
