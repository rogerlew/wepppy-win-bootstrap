# Native Windows WEPP 261029 revision 7

Validated November 5, 2026. The new pair is available by explicit Windows x86_64
selection; the default `wepp_261027`, its compatibility alias and the separate
legacy revegetation selection remain unchanged. No deployment is performed.

```powershell
python scripts/run_project.py "C:\WEPP\my-project" --wepp_exec wepp_261029 --numcpu 1
```

## Build and identity

Native host: blarhg. Toolchain: WinLibs GNU Fortran/GCC 13.3.0 UCRT with MSYS2
build utilities and static GNU linkage. No WSL or IFX. Model source is unchanged:
`e0abe0581f77c6f66917e90daf8f8f429e9315c8` on canonical branch
`wepp_260430_negmeltfix_comparator`. This is model artifact revision 7 and Windows
platform-artifact revision 1, not a new Linux numerical baseline.

| Executable | SHA256 |
| --- | --- |
| `bin/wepp_261029.exe` | `9d7b34295e7fda97de9804b142d11604c404c548f9987e30f59af273f4747107` |
| `bin/wepp_261029_hill.exe` | `a1476ca5be83be3af429124426bee14511b4f1e8e93d17868395c50bad131d97` |

The matching `.exe.json` sidecars preserve source, compiler, capacity and validation
provenance. The registry checks both hashes before clearing output directories;
independent hillslope overrides and arbitrary executable paths remain unsupported.
This release is registered for Windows x86_64 only in this bootstrap.

Windows watershed capacity remains 4,500 hillslopes / 1,500 channels / 6,000
elements; hillslope capacity is 32 OFEs. Static BSS is approximately 183 MiB for
watershed and 2.32 MiB for hill, excluding runtime memory. Imports are Windows
system/UCRT DLLs only; separately installed GNU runtime DLLs are unnecessary.

## Parity and release gates

The fixed Linux revision-7 reference hashes are watershed
`4a9da3980d1a9249e566626c01de920de7dba5088ec25324dc1c6dd6eff8c825` and hill
`210d48da09ff60707ba2404dd32af1f0a74e95437d2cb900c5408121141a1936`.

| Check | Result |
| --- | --- |
| Quick paired daily/hourly controls | 20 executions per platform; 130/130 output files identical |
| Expanded release suite, including all 31 watchlist cases | 51 executions per platform; 347/347 output files identical |
| Small-suite inputs | 571 hashes verified on both platforms |
| Medium watershed | 491 fresh hillslopes, 211 channels, all nine years 2016–2024; 3,443/3,443 output files identical |
| Medium inputs | All 2,468 hashes identical |
| Semantic validation | Complete calendars, finite channel values, valid source metadata, outlet calendar through 2024-12-31 |
| Linux baseline gates | 1,752 tests, both host smokes, 31 watchlist cases, artifact policy and ELF loader checks pass |

The only allowed output normalization is CRLF to LF. No files, columns or numeric
differences were excluded, and each platform generated its own PASS files.
The quick check is a subset of the expanded suite. Native tests and smoke counts
must not be added to output-file counts or interpreted as field validation.

[Source release commit fb5c4af03](https://github.com/wepp-in-the-woods/wepp-forest/commit/fb5c4af03)
retains exact build commands, archived-source identity, build logs, PE inspection,
input/output inventories, run receipts and Linux regression evidence. Local
summaries: [parity](windows-release-261029/parity-comparison.json),
[quick check](windows-release-261029/quick-comparison.json),
[provenance](windows-release-261029/provenance.json), and
[Windows semantic check](windows-release-261029/windows-medium-validation.json).

## Bootstrap integration and limits

The native bootstrap command is exercised using explicit 261029 selection on a
fresh four-year single-OFE paired case, through `totalwatsed2.csv`. Packaging and
selection tests check the new pair and preservation of existing defaults.
The [native command receipt](windows-release-261029/bootstrap-receipt.json)
confirms 1,461 daily rows, 26 numeric columns, a complete 1980–1983 calendar and
finite values. The CSV has its established four-line title/area preamble.
Linux packaging tests pass (21 run, two Windows-only cases skipped); native
Windows tests pass (all 21, no skips). Compressed native
command/test logs and the Linux test log accompany the receipt.

Parity is established for the declared fixtures and pinned toolchains, not every
possible floating-point path or maximum compiled capacity. Specialized RAP
full-history cross-platform equivalence is not claimed. Existing revision-7
scientific, physiological and graphics-field limitations remain in its sidecars.
The Linux binary is not rebuilt or replaced, and old output directories are not
silently regenerated as part of vendoring. Users must run the complete matched
hill/PASS/watershed chain when adopting this pair.
