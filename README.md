# wepppy-win-bootstrap
Acquire and Run weppcloud projects on Windows

This project assumes:
  - You are on windows
  - You have perl installed as C:\Perl64\bin\perl.exe
    - If not change the perl_exe in the run_project.py
  - You have Python3 installed
    - If you want to run the wy_calc postprocessing you will need numpy, scipy, pandas
    
    
## Downloading a project

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

The pmetpara prepation can be enabled by providing the --pmetpara_prep flag. The parameters are hard coded in the run_project.py script. `mid_season_crop_coeff` and `p_coeff` can be float values or dictionaries with the plant loop names and values cooresponding to the coefficients.

### phosphorus.txt prep

The phosphorus prepation can be enabled by providing the --phosphorus_prep flag. The parameters are hard coded in the run_project.py script.

