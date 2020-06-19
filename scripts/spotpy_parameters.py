import os
from os.path import join as _join
from os.path import exists
from os.path import split as _split

import csv

from spotpy import parameter

_thisdir = os.path.dirname(__file__)
_par_dir = _join(_thisdir, 'spotpy_parameterization')

_chn_template = """\
99.1
{nchan}
4
1.500000
{chn_stubs}"""

_chn_stub = """\
Waterway channel with rock base
**Make sure erodibility and shear stress match soil file
Bill Eliot based on L. Tysdal 2/98
2
1
1
0
{chnz} {chnnbr}
{chnn} {chnk} {chntcr} {chnedm} {chneds}
{ctlslp} {ctlz} {ctln}
"""


class ChannelParameters:
    def __init__(self):
        fn = _join(_par_dir, 'channel_pars.csv')
        
        fp = open(fn)
        csv_rdr = csv.DictReader(fp)
        
        pars = {}
        pars_list = []
        for row in csv_rdr:
            par = row['parameter']
            optimize = int(row['optimize'])
            optguess = float(row['optguess'])
            
            if optimize == 0: # fixed parameter
                pars[par] = optguess
                
            else:
                pars[par] = '{%s}' % par
                distribution = row['distribution']
                if distribution.lower() != 'uniform':
                    raise NotImplementedError
                
                low = float(row['low'])
                high = float(row['high'])
                stepsize = row['stepsize']
                if len(stepsize) == 0:
                    stepsize = None
                else:
                    stepsize = float(stepsize)
                    
                if stepsize is None:
                    pars_list.append(parameter.Uniform(name=par, low=low, high=high, optguess=optguess))
                else:
                    pars_list.append(parameter.Uniform(name=par, low=low, high=high, optguess=optguess, stepsize=stepsize))
                
                
        fp.close()
        self.pars = pars
        self.pars_list = pars_list
        
    def create_template_file(self, nchan, dst_fn):
        chn_stub = _chn_stub.format(**self.pars)
        chn_txt = _chn_template.format(nchan=nchan, chn_stubs=chn_stub * nchan)
        
        with open(dst_fn, 'w') as fp:
            fp.write(chn_txt)
            
        assert exists(dst_fn)
        
        
        
        
if __name__ == "__main__":
    from pprint import pprint
    chn_pars = ChannelParameters()
    
    chn_pars.create_template_file(11, 'spotpy_tests/chn_template.txt')
    
        