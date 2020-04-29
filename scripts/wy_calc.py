import pandas as pd
import csv
import os

def wy_calc(start_year, out_dir):
    cwd = os.getcwd()
    
    try:
        os.chdir(out_dir)
        
        # put contents here
        
        
        os.chdir(cwd)
    except:
        os.chdir(cwd)
        raise
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('wd', type=str,   
                        help='path of project')
    parser.add_argument('--wy_calc_start_year',   type=int, 
                        help='run WY Calc postprocessing routine', action='store_true')    
    args = parser.parse_args()

    wd = args.wd
    wy_calc_start_year = args.wy_calc_start_year
    
    wy_calc(wy_calc_start_year, _join(wd, 'wepp/output'))