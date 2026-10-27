# wepppy-win-bootstrap
Acquire and Run weppcloud projects on Windows

## Current WEPP bootstrap binary contract

The default release is **wepp_261027** on Windows and Linux x86_64. Both platforms
use a matched watershed/hillslope pair built with GNU Fortran/GCC 13.3.0. Windows
does not require WSL or a separately installed GNU runtime. Linux requires the
system loader `/lib64/ld-linux-x86-64.so.2` and compatible runtime libraries
including `libgfortran.so.5` (validated on Ubuntu 24.04).

| Platform | Watershed | Hillslope | Watershed capacity |
| --- | --- | --- | --- |
| Windows x86_64 | `bin/wepp_261027.exe` | `bin/wepp_261027_hill.exe` | 4,500 hillslopes / 1,500 channels |
| Linux x86_64 | `bin/wepp_261027` | `bin/wepp_261027_hill` | 45,000 hillslopes / 15,000 channels |

Both hillslope executables support 32 OFEs. Each binary has a JSON provenance and
checksum sidecar. `bin/wepppy-win-bootstrap.exe` remains a byte-identical Windows
watershed alias. Windows 261010 and 261026 are not distributed.

Regenerate hillslope PASS files before watershed runs; do not mix releases.
Validation includes 491 fresh hillslopes and a 211-channel watershed over the
complete 2016–2024 period. All 3,443 model output files match between these
platforms after line-ending normalization only. See
[release validation](docs/windows-release-261027.md).
Use `--numcpu 1` for a conservative memory/concurrency setting. Windows watershed
static BSS is approximately 183 MiB; Linux's larger capacity requires more memory.

Python 3 with numpy and pandas is required; optional WY postprocessing also
requires scipy. macOS ARM64 retains its legacy bundled default; 261027 is not
provided for macOS or Linux ARM64. The revegetation option selects a separate
legacy Windows release.
## JWT Authentication (PowerUsers)

Some projects require JWT authentication to download. PowerUsers can obtain a JWT
token from their profile page on WEPPcloud (accessible from the Interfaces page or
from the "More" dropdown menu).

To request PowerUser status, email rogerlew@uidaho.edu.

### Setup

Save your JWT token to the file `~/.weppcloud_jwt`:

- **Windows:** `%USERPROFILE%\.weppcloud_jwt`
- **Mac/Linux:** `~/.weppcloud_jwt`

The file should contain only the JWT token string (no quotes, no extra whitespace).

The download scripts will automatically detect and use the token when the file exists.
If the file is not present, the scripts will download without authentication (which
will work for public projects).

## Downloading a project with aria2c

Use [wget_download_weppcloud_project_noprep.bat](scripts/wget_download_weppcloud_project_noprep.bat)
on Windows. The wrapper uses Python's standard library to fetch
`/weppcloud/runs/<run_id>/cfg/aria2c.spec`; bundled `aria2c.exe` downloads the listed
files with up to 10 concurrent downloads. The shell wrapper uses the same Python
client and an installed `aria2c`.

From PowerShell or Command Prompt, change to the repository's `scripts` directory
with Python available on PATH (activate your Python/Conda environment first).
Replace `YOUR_RUN_ID` with a current run ID; quote destination paths with spaces:

```powershell
cd scripts
.\wget_download_weppcloud_project_noprep.bat YOUR_RUN_ID C:\WEPP\YOUR_RUN_ID
```

The script downloads existing project files as is; it does not generate exports.
If you need exports, generate them in WEPPcloud before downloading. The old
recursive-wget preparation script has been removed because it used a legacy
prep-details endpoint and crawled HTML browse pages.

### Checking the download

Check that aria2c reports completed downloads, the script exits with code 0, and
the expected files exist. Failed manifest requests print the server's explanation,
error code and request ID when supplied, return nonzero and never launch aria2c.
A validated inventory remains available as `<run_id>_aria2c.spec` in the current
directory. aria2c consumes a private copy of the current response, preventing
reuse of an earlier failed/stale response.
An actual empty HTTP 200 manifest is reported explicitly as an empty project.

Failed file transfers retain aria2c's nonzero exit and partial download files.
The client rechecks up to ten failed URLs with a one-byte range request (ten-second
socket inactivity timeout each) to obtain HTTP error details that aria2c does not display. If a
recheck succeeds, the original download still counts as failed. Rerunning the
command uses aria2c's existing resume behavior. Diagnostic responses are bounded
to 8 KiB; credentials and terminal control characters are removed from messages.

- **HTTP 401:** Check the JWT setup above and your access to the run.
- **HTTP 404:** Verify the run ID and manifest URL.
- **HTTP 500:** Report the displayed message, error code and request ID. For
  `server_configuration_error`, the service operator must repair the named
  configuration; changing the project or refreshing the user's token will not
  repair a missing server secret. Never send your JWT to support.
- **Timeout or interrupted transfer:** The command fails; check connectivity and
  retry. A server/proxy that provides no diagnostic body is reported explicitly.

October 27 validation exercises local HTTP failures and exact-byte successful
downloads using native Windows Python and the bundled aria2c, including space
and Unicode filenames. This is client validation, not a production deployment
claim. Regression command: `python -m unittest discover -s tests -v`.

## Legacy Python downloader

[download_weppcloud_project.py](scripts/download_weppcloud_project.py) still uses
the legacy `/weppcloud/runs/<run_id>/0/archive/` endpoint. HTTP 404 failures have
been reported with this downloader; use the aria2c workflow above for project
downloads.

The legacy client also prints HTTP failure details and returns nonzero before
writing or extracting an archive; its endpoint selection is unchanged.

## Running a project

Use the run_project.py script to run wepp. By default it runs the hillslopes in parallel.

e.g.
```
python3 run_project.py C:\Users\roger\rlew-mucky-pepperoni
```

Some versions of WEPP will crash if multiple executables are trying to write to the same file (e.g. fort.80). If this occurs disable multiprocessing with the --no_multiprocesing flag

e.g.
```
python3 run_project.py C:\Users\roger\rlew-mucky-pepperoni --no_multiprocessing
```

To run the wy_calc post processing provide --wy_calc_start_year <start_year>
e.g.
```
python3 run_project.py C:\Users\roger\rlew-mucky-pepperoni --wy_calc_start_year 1989
```

### Selecting the WEPP executable

Use `--wepp_exec RELEASE` to select a **matched watershed and hillslope release**.
The default is `wepp_261027` on Windows and Linux x86_64, so this argument is
optional. `--wepp-exec` is an equivalent spelling.

Run these examples from the repository root. On Windows:

```powershell
python scripts/run_project.py "C:\WEPP\my-project" --wepp_exec wepp_261027 --numcpu 1
```

On Linux:

```bash
python scripts/run_project.py ~/runs/my-project --wepp_exec wepp_261027 --numcpu 1
```

Omitting `--wepp_exec wepp_261027` selects the same pair on either platform.
Use the release name without `.exe` or a filesystem path. The runner selects
both platform-specific binaries automatically and prints their paths.

| Release name | Supported platform | Selection |
| --- | --- | --- |
| `wepp_261027` | Windows and Linux x86_64 | Default matched watershed/hillslope pair |
| `wepp_reveg` | Windows x86_64 | Legacy revegetation executable for both modes |
| `wepp.arm64.mac` | macOS ARM64 | Legacy default executable for both modes |

There is no `--wepp_hill_exec` option: the hillslope binary cannot be selected
independently. Both binaries must match the release's pinned SHA-256 checksums.
An unsupported release, missing binary or checksum mismatch fails before existing
outputs are cleared. Regenerate hillslope PASS files with the selected release;
do not reuse PASS files from another build.

`--revegetation` remains a Windows alias for selecting `wepp_reveg` and cannot
be combined with `--wepp_exec`. New releases must have both binaries validated
and registered together in `scripts/wepp_executables.py` before they can be
selected.
### Running Reveg for 9005 Soils

To run the reveg wepp binary provide --revegetation

```
python run_project.py C:\Users\roger\Downloads\reasonable-acquirer --revegetation
```

### pmetpara.txt prep

The pmetpara preparation can be enabled by providing the --pmetpara_prep flag. The parameters are hard coded in the run_project.py script. `mid_season_crop_coeff` and `p_coeff` can be float values or dictionaries with the plant loop names and values cooresponding to the coefficients. See line 156 of run_project.py

### phosphorus.txt prep

The phosphorus preparation can be enabled by providing the --phosphorus_prep flag. The parameters are hard coded in the run_project.py script. See line 159 of run_project.py

### gwcoeff.txt prep

The gwcoeff preparation can be enabled by providing the --gwcoeff_prep flag. The parameters are hard coded in the run_project.py script. See line 162 of run_project.py

```
python.exe .\run_project.py C:\Users\roger\Downloads\lt_obs_Blackwood_BC1_10336660_CurCond.2020.cl532.observed.ki5krcs.no_pmet.wepp_ui --wy_calc_start_year 1989 --pmetpara_prep --phosphorus_prep --gwcoeff_prep
```

### Anu WEPP Management Mod

Adds a fourth parameter 0.0000 to the last line of the plant cropland loop

```
python.exe .\run_project.py C:\Users\roger\Downloads\lt_obs_Blackwood_BC1_10336660_CurCond.2020.cl532.observed.ki5krcs.no_pmet.wepp_ui --wy_calc_start_year 1989 --pmetpara_prep --phosphorus_prep --gwcoeff_prep --anu_man_mod
```

# Mac OS-X Apple Silicon


### install curl and aria2c
```
brew install aria2c
```

### install anaconda
```
brew install --cask anaconda
/opt/homebrew/anaconda3/bin/conda init zsh
source ~/.zshrc
```

# Ubuntu

### install curl and aria2
```
sudo apt install curl aria2
```

## Download project with aria2c

Replace `YOUR_RUN_ID` with a current run ID. The shell script uses curl to fetch
the manifest and aria2c to download its files. The JWT setup and manifest
troubleshooting above also apply.

```bash
cd scripts
bash ./wget_download_weppcloud_project.sh YOUR_RUN_ID ~/runs/YOUR_RUN_ID
```

## run project
```
 python run_project.py ~/runs/unsupported-watercolor
```

## License

Repository-authored code is licensed under the [MIT License](LICENSE).
Bundled third-party code, executables, and datasets retain their respective
license terms and copyright notices.
