# Reproduction

Use isolated directories; never extract over a working source checkout. The
scripts in artifacts/ retain the actual commands used and expect the temporary
roots shown in findings.md. They are experimental campaign utilities, not a
bootstrap installer. Each replay destination must be fresh.

1. Read artifacts/provenance.json. Use git archive at each recorded commit with
   its archive_paths list to produce /tmp/native-parity-20261027/TAG/source.tar.
   Verify its SHA-256. Copy the archives to the same C:/tmp root on blarhg.
2. Restore the input generator and committed fixtures from source commit
   d354e3c998f81955f9d9e5ca7d01ca56e1a9f04b. The retained stage-wepp-parity.py
   shows the original construction. Select single-daily and watch-p24, retain
   only hill cards, preserve shared files, and verify artifacts/inputs.json.
   Seed TAG/baseline-cases with fresh runs/ and empty output/ per case. The
   parity-stage.py helper then creates additional fresh lane directories.
3. Copy parity-*.py and parity-build-20261027.sh to /tmp on Linux and C:/tmp on
   blarhg. Use bash parity-build-20261027.sh PLATFORM TAG LANE. Platforms are
   linux/windows; lanes used were baseline, diagnostic, observe,
   observe-radiation, crop-checked, radtrig and watershed. See build logs and
   binary manifests for which combinations ran. On Windows invoke the build
   script with C:/msys64/usr/bin/bash.exe and Windows Python for replay.
4. Run run_windows_release_cases.py ROOT --hill BINARY --watershed BINARY.
   The selected manifests contain only hill cards, so the second argument is
   a required placeholder; no watershed simulation is implied. Each run uses
   fresh outputs, LC_ALL=C and TZ=UTC, validates exit status and success markers,
   and rejects recognized runtime errors. Use the unchanged released Linux
   executable for reference-cases. Diagnostic failures are expected evidence.
5. The observation script modifies only snapshot copies. It gates logging on
   wepp_observe.on, restricts the trace to days 50–53 and records hexadecimal
   float32 representations. Patches preserve the exact instrumentation and the
   two separate behavioral experiments. Never combine the crop and radtrig
   patches when reproducing these lanes.
6. Compile parity-radcur-probe.f90 with parity-radcur.for using each compiler,
   -O2 -ffp-contract=off, and -static on Windows. Compare the retained text
   outputs. This small probe reproduces the radiation discrepancy independently
   of WEPP input parsing, COMMON blocks and the long model replay.
7. Use parity-collect.py to transfer output evidence from blarhg, and
   parity-compare-summary.py with compare_wepp_raw_outputs from d354e3c. The
   latter compares successful executions only; failed diagnostic cases are
   reported through their separate runtime receipts, never treated as parity.

For validation of the comparator itself:

```sh
python -m pytest -q /tmp/wepp-windows-261021-20261026/tests/test_compare_wepp_raw_outputs.py
```

Result: three passed. See findings.md for release gates intentionally deferred
because the numerical and full-capacity build prerequisites failed.
