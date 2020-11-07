# wepppy-win-bootstrap
Acquire and Run weppcloud projects on Windows

This project assumes:
  - You are on windows
  - You have perl installed as C:\Perl64\bin\perl.exe
    - If not change the perl_exe in the run_project.py
  - You have Python3 installed
    - If you want to run the wy_calc postprocessing you will need numpy, scipy, pandas
    
    
## Downloading a project with wget
Use the wget_download_weppcloud_project.py script and provide the run_id and local destination directory as arguments. The included wget.exe must be in your path if the batch file is called from outside of the scripts folder.

e.g.
```
./wget_download_weppcloud_project.bat rlew-mucky-pepperoni C:\Users\roger\
```
## Downloading a project with python script

Use the download_weppcloud_project.py script and provide the run_id and local destination directory as arguments

e.g.
```
python3 download_weppcloud_project.py rlew-mucky-pepperoni C:\Users\roger\
```

This will download the zip to C:\Users\roger\rlew-mucky-pepperoni.zip and extract the project to C:\Users\roger\rlew-mucky-pepperoni

To not extract the project provide the --no_extract flag

e.g.
```
python3 download_weppcloud_project.py rlew-mucky-pepperoni C:\Users\roger\ --no_extract
```

To not remove the zip after extracting provide the --remove flag

```
python3 download_weppcloud_project.py rlew-mucky-pepperoni C:\Users\roger\ --remove
```

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

# Observed
