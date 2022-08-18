# Copyright (c) 2016-2018, University of Idaho
# All rights reserved.
#
# Roger Lew (rogerlew@gmail.com)
#
# The project described was supported by NSF award number IIA-1301792
# from the NSF Idaho EPSCoR Program and by the National Science Foundation.

from os.path import exists as _exists
from os.path import join as _join
from os.path import split as _split

from copy import deepcopy
from collections import OrderedDict
import csv
import math
from datetime import datetime, timedelta
from glob import glob
from multiprocessing import Pool
import numpy as np
import pandas as pd

from all_your_base import determine_wateryear

NCPU = 2


def _read_hill_wat_sed(pass_fn):
    from .hill_pass import HillPass
    from .hill_wat import HillWat

    wat_fn = pass_fn.replace('.pass.dat', '.wat.dat')
    hill_wat = HillWat(wat_fn)
    watbal = hill_wat.calculate_daily_watbal()

    hill_pass = HillPass(pass_fn)
    sed_df = hill_pass.sed_df
 
    for col in sed_df.columns:
        if col in ['Julian', 'Year', 'Area (ha)']:
            continue
        watbal[col] = sed_df[col]

    return watbal, hill_wat.total_area


class TotalWatSed2(object):
    def __init__(self, wd, baseflow_opts=None, phos_opts=None):

        if baseflow_opts is None:
            from wepppy.nodb import Ron, Wepp
            wepp = Wepp.getInstance(wd)
            baseflow_opts = wepp.baseflow_opts

        if baseflow_opts is None:
            from wepppy.nodb import Ron, Wepp
            wepp = Wepp.getInstance(wd)
            if wepp.has_phosphorus:
                phos_opts = wepp.phosphorus_opts

        output_dir = _join(wd, 'wepp/output')
        pkl_fn = _join(output_dir, 'totwatsed2.pkl')
        if _exists(pkl_fn):
            self.d = pd.read_pickle(pkl_fn)
            self.wsarea = self.d.attrs['wsarea']
            return

        pass_fns = glob(_join(output_dir, 'H*.pass.dat'))
        
        pool = Pool(processes=NCPU)
        results = pool.map(_read_hill_wat_sed, pass_fns)
        pool.close()

        d = None
        totarea_m2 = 0.0
        for watsed, area in results:
            totarea_m2 += area

            if d is None:
                d = deepcopy(watsed)
            else:
                for col in watsed.columns:
                    if col in ['Year', 'Month', 'Day', 'Julian']:
                        continue
                    d[col] += watsed[col]

        totarea_ha = totarea_m2 / 10000.0


        d['Cumulative Sed Del (tonnes)'] = np.cumsum(d['Sed Del (kg)'] / 1000.0)
        d['Sed Del Density (tonne/ha)'] = (d['Sed Del (kg)'] / 1000.0) / totarea_ha
        d['Precipitation (mm)'] = d['P (m^3)'] / totarea_m2 * 1000.0
        d['Rain + Melt (mm)'] = d['RM (m^3)'] / totarea_m2 * 1000.0
        d['Transpiration (mm)'] = d['Ep (m^3)'] / totarea_m2 * 1000.0
        d['Evaporation (mm)'] = d['Es+Er (m^3)'] / totarea_m2 * 1000.0
        d['ET (mm)'] = d['Evaporation (mm)'] + d['Transpiration (mm)']
        d['Percolation (mm)'] = d['Dp (m^3)'] / totarea_m2 * 1000.0
        d['Runoff (mm)'] = d['QOFE (m^3)'] / totarea_m2 * 1000.0
        d['Lateral Flow (mm)'] = d['latqcc (m^3)'] / totarea_m2 * 1000.0
        d['Storage (mm)'] = d['Total-Soil Water (m^3)'] / totarea_m2 * 1000.0

        # calculate Res volume, baseflow, and aquifer losses
        _res_vol = np.zeros(d.shape[0])
        _res_vol[0] = baseflow_opts.gwstorage
        _baseflow = np.zeros(d.shape[0])
        _aq_losses = np.zeros(d.shape[0])

        for i, perc in enumerate(d['Percolation (mm)']):
            if i == 0:
                continue

            _aq_losses[i-1] = _res_vol[i-1] * baseflow_opts.dscoeff
            _res_vol[i] = _res_vol[i-1] - _baseflow[i-1] + perc - _aq_losses[i-1]
            _baseflow[i] = _res_vol[i] * baseflow_opts.bfcoeff

        d['Reservoir Volume (mm)'] = _res_vol
        d['Baseflow (mm)'] = _baseflow
        d['Aquifer Losses (mm)'] = _aq_losses

        d['Streamflow (mm)'] = d['Runoff (mm)'] + d['Lateral Flow (mm)'] + d['Baseflow (mm)']

        if phos_opts is not None:
            assert isinstance(phos_opts, PhosphorusOpts)
            if phos_opts.isvalid:
                d['P Load (mg)'] = d['Sed. Del (kg)'] * phos_opts.sediment
                d['P Runoff (mg)'] = d['Runoff (mm)'] * phos_opts.surf_runoff * totarea_ha 
                d['P Lateral (mg)'] = d['Lateral Flow (mm)'] * phos_opts.lateral_flow * totarea_ha
                d['P Baseflow (mg)'] = d['Baseflow (mm)'] * phos_opts.baseflow * totarea_ha
                d['Total P (kg)'] = (d['P Load (mg)'] +
                                     d['P Runoff (mg)'] +
                                     d['P Lateral (mg)'] +
                                     d['P Baseflow (mg)']) / 1000.0 / 1000.0
                d['Particulate P (kg)'] = d['P Load (mg)'] / 1000000.0
                d['Soluble Reactive P (kg)'] = d['Total P (kg)'] - d['Particulate P (kg)']

                d['P Total (kg/ha)'] = d['Total P (kg)'] / totarea_ha
                d['Particulate P (kg/ha)'] = d['Particulate P (kg)'] / totarea_ha
                d['Soluble Reactive P (kg/ha)'] = d['Soluble Reactive P (kg)'] / totarea_ha

        # Determine Water Year Column
        _wy = np.zeros(d.shape[0], dtype=np.int)
        for i, (j, y) in enumerate(zip(d['Julian'], d['Year'])):
            _wy[i] = determine_wateryear(y, j=j)
        d['Water Year'] = _wy

        d.attrs['wsarea'] = totarea_m2
        d.to_pickle(pkl_fn)

        self.wsarea = totarea_m2
        self.d = d

    @property
    def num_years(self):
        return len(set(self.d['Year']))

    @property
    def sed_delivery(self):
        return np.sum(self.d['Sed Del (kg)'])

    @property
    def class_fractions(self):
        d = self.d

        sed_delivery = self.sed_delivery

        if sed_delivery == 0.0:
            return [0.0, 0.0, 0.0, 0.0, 0.0]

        return [np.sum(d['Sed Del c1 (kg)']) / sed_delivery,
                np.sum(d['Sed Del c2 (kg)']) / sed_delivery,
                np.sum(d['Sed Del c3 (kg)']) / sed_delivery,
                np.sum(d['Sed Del c4 (kg)']) / sed_delivery,
                np.sum(d['Sed Del c5 (kg)']) / sed_delivery]

    def export(self, fn):
        d = self.d
        for k in d.keys():
            if '(m^3)' in k:
                del d[k]

        with open(fn, 'w') as fp:
            fp.write('DAILY TOTAL WATER BALANCE AND SEDIMENT\n\n')
            fp.write(f'Total Area (m^2): {self.wsarea}\n\n')

            wtr = csv.DictWriter(fp,
                                 fieldnames=list(d.keys()),
                                 lineterminator='\n')
            wtr.writeheader()
            for i, yr in enumerate(d['Year']):
                wtr.writerow(OrderedDict([(k, d[k][i]) for k in d]))
