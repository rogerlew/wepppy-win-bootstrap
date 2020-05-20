import os
from os.path import join as _join
from os.path import split as _split
from os.path import exists as _exists

from glob import glob

import shutil

import managements
from managements import Management

managements.__dict__['VERSION'] = 'anu'

def anu_wepp_management_mod(runs_dir):
    plant_loops = set()
    man_fns = glob(_join(runs_dir, '*.man'))
    
    backup_dir = _join(runs_dir, 'original_mans')
    if not _exists(backup_dir):
        os.mkdir(backup_dir)
        
        for man_fn in man_fns:
            _fn = _split(man_fn)[-1]
            if 'pw0' in _fn:
                continue
            
            _man_fn = _join(backup_dir, _fn)
            shutil.move(man_fn, _man_fn)
            
    for man_fn in man_fns:
        _fn = _split(man_fn)[-1]
        if 'pw0' in _fn:
            continue
        
        man = Management(Key=None,
                         ManagementFile=_fn, 
                         ManagementDir=backup_dir,
                         Description='-',
                         Color=(0,0,0,0))
                         
        with open(man_fn, 'w') as fp:
            fp.write(str(man))
        
if __name__ == "__main__":
    anu_wepp_management_mod(r'C:\Users\roger\Downloads\man_chg')