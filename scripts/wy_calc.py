import pandas as pd
import csv
import os

def wy_calc(start_year, out_dir):
    cwd = os.getcwd()
    
    try:
        os.chdir(out_dir)
        
        names = "Day Month Year Precip. Runoff Peak Sediment Solub. Particulate Total".split()
        df = pd.read_csv('ebe_pw0.txt', delim_whitespace=True, names=names, skiprows=9)

        df_list = []

        for index, row in df.iterrows():
            
            row["Year2"] = start_year + row["Year"]
            if row["Month"]>9:
                row["WY"] = row["Year2"]+1
            else:
                row["WY"] = row["Year2"]
            try:
                row["SedimentWY"] = float(row["Sediment"])/1000.0
            except:
                row["SedimentWY"] = 0
               
            df_list.append(row)

        df2 = pd.DataFrame(df_list)

        dfWY = df2.groupby(["WY"])["SedimentWY"].sum()

        dfSRP = df2.groupby(["WY"])["Solub."].sum()
        dfPP = df2.groupby(["WY"])["Particulate"].sum()
        dfTP = df2.groupby(["WY"])["Total"].sum()
        #dfY = df2.groupby(["Year2"])["SedimentWY"].sum()
            
        dfWY.to_csv('WY_sediment.txt')

        dfSRP.to_csv('WY_SRP.txt')
        dfPP.to_csv('WY_PP.txt')
        dfTP.to_csv('WY_TP.txt')
                
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