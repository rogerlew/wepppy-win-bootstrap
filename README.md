# wepppy-win-bootstrap
Acquire and Run weppcloud projects on Windows

## Current WEPP bootstrap binary contract

- Current bootstrap source lineage: `wepp_260430`.
- Required binary filename in this repo: `bin/wepppy-win-bootstrap.exe`.
- Build host for this lane: `blarhg` (Windows).

If you rebuild from `wepp_260430`, publish the executable with this exact name;
`scripts/run_project.py` resolves this fixed path/name.

This project assumes:
  - You are on windows
  - You have Python3 installed
    - If you want to run the wy_calc postprocessing you will need numpy, scipy, pandas

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
on Windows. Despite its name, this script uses the bundled `wget.exe` only to fetch
`/weppcloud/runs/<run_id>/cfg/aria2c.spec`; `aria2c.exe` downloads the files listed
in that manifest with up to 10 concurrent downloads.

From PowerShell or Command Prompt, change to the repository's `scripts` directory
so the bundled executables can be found. Replace `YOUR_RUN_ID` with a current run
ID and choose a destination path without spaces:

```powershell
cd scripts
.\wget_download_weppcloud_project_noprep.bat YOUR_RUN_ID C:\WEPP\YOUR_RUN_ID
```

The script downloads existing project files as is; it does not generate exports.
If you need exports, generate them in WEPPcloud before downloading. The old
recursive-wget preparation script has been removed because it used a legacy
prep-details endpoint and crawled HTML browse pages.

### Checking the download

Check that the manifest request succeeds, aria2c reports completed downloads,
and the expected project files exist in the destination. The batch script
currently continues after a failed manifest request and can return exit code 0
with `No files to download`; that message alone does not confirm success.

- **HTTP 401:** Check the JWT setup above and your access to the run.
- **HTTP 404:** Verify the run ID and manifest URL.
- **HTTP 500 or a stalled manifest request:** Report the run URL and downloader
  output so the server request can be investigated. aria2c cannot download the
  project until a valid manifest is available.

Windows validation on October 26, 2026 reached the manifest request for
`animal-misgiving` using JWT authentication, but the request stalled. A separate
curl request timed out after 45 seconds without receiving data. A successful
end-to-end download has not yet been verified.

## Legacy Python downloader

[download_weppcloud_project.py](scripts/download_weppcloud_project.py) still uses
the legacy `/weppcloud/runs/<run_id>/0/archive/` endpoint. HTTP 404 failures have
been reported with this downloader; use the aria2c workflow above for project
downloads.

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

### Running Reveg for 9005 Soils

To run the reveg wepp binary provide --reveg

```
python run_project.py C:\Users\roger\Downloads\reasonable-acquirer --reveg
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
