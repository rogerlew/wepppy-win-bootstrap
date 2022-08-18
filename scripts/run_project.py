import sys
from glob import glob
import os
from os.path import join as _join
from os.path import split as _split
from os.path import exists
from time import time
import argparse
import subprocess
import multiprocessing
import shutil

from concurrent.futures import (
    ThreadPoolExecutor, 
    as_completed, 
    wait, 
    FIRST_EXCEPTION
)
from all_your_base import isint
from wy_calc import wy_calc
from phosphorus_prep import phosphorus_prep
from pmetpara_prep import pmetpara_prep
from gwcoeff_prep import gwcoeff_prep
from anu_wepp_management_mod import anu_wepp_management_mod
from totalwatsed import TotalWatSed2
from nodb_stubs import BaseflowOpts, PhosphorusOpts

NCPU = multiprocessing.cpu_count() - 1
if NCPU < 1:
    NCPU = 1
    
USE_MULTIPROCESSING = True

wepp_exe = "../bin/wepppy-win-bootstrap.exe"

def get_baseflow_opts(runs_dir):
    fn = _join(runs_dir, 'gwcoeff.txt')
    if not exists(fn):
        return None
    
    with open(fn, 'r') as fp:
        lines = fp.readlines()
    
    gwstorage = float(lines[0].split()[0]) 
    bfcoeff = float(lines[1].split()[0]) 
    dscoeff = float(lines[2].split()[0]) 
    bfthreshold = float(lines[3].split()[0]) 
    return BaseflowOpts(gwstorage=gwstorage, bfcoeff=bfcoeff, dscoeff=dscoeff, bfthreshold=bfthreshold)
 
    
def get_phosphorus_opts(runs_dir):
    fn = _join(runs_dir, 'phosphorus.txt')
    if not exists(fn):
        return None
    
    with open(fn, 'r') as fp:
        lines = fp.readlines()
    
    surf_runoff = float(lines[0].split()[0]) 
    lateral_flow = float(lines[1].split()[0]) 
    baseflow = float(lines[2].split()[0]) 
    sediment = float(lines[3].split()[0]) 
    return PhosphorusOpts(surf_runoff=surf_runoff, lateral_flow=lateral_flow, baseflow=baseflow, sediment=sediment)
        
    
def run_hillslope(wepp_id, runs_dir):
    t0 = time()

    cmd = [os.path.abspath(wepp_exe)]

    assert exists(_join(runs_dir, 'p%i.man' % wepp_id))
    assert exists(_join(runs_dir, 'p%i.slp' % wepp_id))
    assert exists(_join(runs_dir, 'p%i.cli' % wepp_id))
    assert exists(_join(runs_dir, 'p%i.sol' % wepp_id))

    _run = open(_join(runs_dir, 'p%i.run' % wepp_id))
    _log = open(_join(runs_dir, 'p%i.err' % wepp_id), 'w')

    p = subprocess.Popen(cmd, stdin=_run, stdout=_log, stderr=_log, cwd=runs_dir)
    p.wait()
    _run.close()
    _log.close()

    log_fn = _join(runs_dir, 'p%i.err' % wepp_id)
    with open(log_fn) as fp:
        lines = fp.readlines()
        for L in lines:
            if 'WEPP COMPLETED HILLSLOPE SIMULATION SUCCESSFULLY' in L:
                return True, wepp_id, time() - t0

    raise Exception('Error running wepp for wepp_id %i\nSee %s'
                    % (wepp_id, log_fn))


def run_watershed(runs_dir, output_dir):
    print('runs_dir', runs_dir)

    t0 = time()

    cmd = [os.path.abspath(wepp_exe)]

    assert exists(_join(runs_dir, 'pw0.str'))
    assert exists(_join(runs_dir, 'pw0.chn'))
    assert exists(_join(runs_dir, 'pw0.imp'))
    assert exists(_join(runs_dir, 'pw0.man'))
    assert exists(_join(runs_dir, 'pw0.slp'))
    assert exists(_join(runs_dir, 'pw0.cli'))
    assert exists(_join(runs_dir, 'pw0.sol'))
    assert exists(_join(runs_dir, 'pw0.run'))

    _run = open(_join(runs_dir, 'pw0.run'))
    _log = open(_join(runs_dir, 'pw0.err'), 'w')

    p = subprocess.Popen(cmd, stdin=_run, stdout=_log, stderr=_log, cwd=runs_dir)
    p.wait()
    _run.close()
    _log.close()

    log_fn = _join(runs_dir, 'pw0.err')

    for fn in glob(_join(runs_dir, '*.out')):
        dst_path = _join(output_dir, _split(fn)[1])
        shutil.move(fn, dst_path)
        
    with open(_join(runs_dir, 'pw0.err')) as fp:
        stdout = fp.read()
        if 'WEPP COMPLETED WATERSHED SIMULATION SUCCESSFULLY' in stdout:
            return True, time() - t0
            
    raise Exception('Error running wepp for watershed \nSee <a href="browse/wepp/runs/pw0.err">%s</a>' % log_fn)


def oncomplete(wepprun):
    status, _id, elapsed_time = wepprun.result()
    assert status
    print('  {} completed run in {}s\n'.format(_id, elapsed_time))

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('wd', type=str,   
                        help='path of project')
    parser.add_argument('-n', '--numcpu',   type=int, 
                        help='Number of cpus in pool    (1)')
    parser.add_argument('--wy_calc_start_year',   type=int, 
                        help='run WY Calc postprocessing routine')   
    parser.add_argument('--no_multiprocessing',
                        help='Disable multiprocessing', action='store_true')    
    parser.add_argument('--pmetpara_prep',
                        help='Build pmetpara.txt', action='store_true')    
    parser.add_argument('--phosphorus_prep',
                        help='Build phosphorus.txt', action='store_true')
    parser.add_argument('--gwcoeff_prep',
                        help='Build gwcoeff.txt', action='store_true')   
    parser.add_argument('--anu_man_mod',
                        help='Modify plant loop parameters for Anu WEPP', action='store_true')   
    args = parser.parse_args()

    wd = args.wd
    numcpu = (args.numcpu, NCPU)[args.numcpu is None]
    wy_calc_start_year = args.wy_calc_start_year
    
    no_multiprocessing = (args.no_multiprocessing, False)[args.no_multiprocessing is None]
    if no_multiprocessing:
        USE_MULTIPROCESSING = False
        
    run_pmetpara_prep = (args.pmetpara_prep, False)[args.pmetpara_prep is None]
    run_phosphorus_prep = (args.phosphorus_prep, False)[args.phosphorus_prep is None]
    run_gwcoeff_prep = (args.gwcoeff_prep, False)[args.gwcoeff_prep is None]
    run_anu_man_mod = (args.anu_man_mod, False)[args.anu_man_mod is None]
    
    print('USE_MULTIPROCESSING', USE_MULTIPROCESSING)
    
    assert not wd.endswith('.py')
    assert exists(wd)

    print('project run_id', wd)

    runs_dir = _join(wd, 'wepp/runs')
    output_dir = _join(wd, 'wepp/output')
    
    assert exists(runs_dir)
    assert exists(output_dir)
    
    if run_pmetpara_prep:
        pmetpara_prep(runs_dir, mid_season_crop_coeff=0.95, p_coeff=0.8)
        
    if run_phosphorus_prep:
        phosphorus_prep(runs_dir, surf_runoff=0.003, lateral_flow=0.004, baseflow=0.005, sediment=1000.0)

    if run_gwcoeff_prep:
        gwcoeff_prep(runs_dir, gwstorage=100, bfcoeff=0.01, dscoeff=0.00, bfthreshold=1.001)
        
    if run_anu_man_mod:
        anu_wepp_management_mod(runs_dir)
        
    hillslope_runs = glob(_join(runs_dir, 'p*.run'))
    hillslope_runs = [run for run in hillslope_runs if 'pw' not in run]
    
    print('cleaning output dir')
    if exists(output_dir):
        shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    if USE_MULTIPROCESSING:
        pool = ThreadPoolExecutor(NCPU)
        futures = []

    for hillslope_run in hillslope_runs:
        
        run_fn = _split(hillslope_run)[-1]
        wepp_id = run_fn.replace('p', '').replace('.run', '')
        assert isint(wepp_id), wepp_id
        
        if USE_MULTIPROCESSING:
            futures.append(pool.submit(lambda p: run_hillslope(*p), (int(wepp_id), runs_dir)))
            futures[-1].add_done_callback(oncomplete)
        else:
            status, _id, elapsed_time = run_hillslope(int(wepp_id), runs_dir)
            assert status
            print('  {} completed run in {}s\n'.format(_id, elapsed_time))

    if USE_MULTIPROCESSING:
        wait(futures, return_when=FIRST_EXCEPTION)
    
    run_watershed(runs_dir, output_dir)
    print('completed watershed run')

    totwatsed = TotalWatSed2(wd, 
                             get_baseflow_opts(runs_dir), 
                             get_phosphorus_opts(runs_dir))
    totwatsed.export(_join(output_dir, 'totalwatsed2.csv'))
    
    if wy_calc_start_year is not None:
        wy_calc(wy_calc_start_year, output_dir)
    
    print('done')
