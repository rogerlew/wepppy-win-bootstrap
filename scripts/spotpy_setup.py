import spotpy
import numpy as np

import os

from os.path import join as _join
from os.path import split as _split
from os.path import exists
import math
import json
from glob import glob
import multiprocessing

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    wait,
    FIRST_EXCEPTION
)

from spotpy.parameter import ParameterSet

from all_your_base import isint
from spotpy_parameters import ChannelParameters
from observed import DailyObserved

from wepp.out import Ebe
from run_project import run_watershed, run_hillslope, oncomplete

_thisdir = os.path.dirname(__file__)
_parsdir = _join(_thisdir, 'spotpy_parameterization')
_templates_dir = _join(_thisdir, 'spotpy_templates')

NCPU = multiprocessing.cpu_count() - 1
if NCPU < 1:
    NCPU = 1

USE_MULTIPROCESSING = False

wd = r'C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast'


class spotpy_setup(object):
    def __init__(self, used_algorithm='default'):
        global wd
        print('wd', wd)

        self._used_algorithm = used_algorithm

        self.params = []

        # Channel Parameters
        chn_fn = _join(_parsdir, 'channel_pars.csv')
        self.chn_pars = ChannelParameters(chn_fn)
        self.params.extend(self.chn_pars.pars_list)
        self.wd = wd
        self.runs_dir = _join(wd, 'wepp/runs')
        self.output_dir = _join(wd, 'wepp/output')

        self.hillslope_runs_required = False
        # TODO toggle hillslope_runs_required based on the params list

        self._load_calib()
        self._load_observed()

    def _load_calib(self):
        calib_fn = _join(self.wd, 'spotpy', 'calibration.json')
        assert exists(calib_fn)
        self.calib = json.load(open(calib_fn))

    def _load_observed(self):

        # TODO: implement transform from calib

        calib = self.calib

        observed_d = {}
        for period in calib:
            if period == 'daily':
                observed_d[period] = {}

                for measure in calib[period]:
                    if measure not in observed_d:
                        observed_d[period][measure] = []

                    for obs in calib[period][measure]:
                        obs_fn = obs['path']
                        observed_d[period][measure].append(obs)
                        observed_d[period][measure][-1]['data'] = DailyObserved(obs_fn)

            elif period == 'annual':
                raise NotImplementedError
            else:
                raise KeyError

        self.observed_d = observed_d

    def evaluation(self):
        return self.observed_d

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    @property
    def nchn(self):
        with open(_join(self.runs_dir, 'pw0.slp')) as fp:
            fp.readline()
            return int(fp.readline())

    def simulation(self, vector):
        d = {}
        if isinstance(vector, ParameterSet):
            print('vector', vector)

            for param in self.params:
                key = param.name
                val = vector[key]
                _type, _name = key.split(':')
                if _type not in d:
                    d[_type] = {}

                d[_type][_name] = val

        else:
            for tup in vector:
                print('tup', tup)
                val = tup[0]
                key = tup[1]
                _type, _name = key.split(':')
                if _type not in d:
                    d[_type] = {}

                d[_type][_name] = val

        if 'chndefs' in d:
            chn_pars = self.chn_pars
            chn_pars.create_template_file(self.nchn, _join(self.runs_dir, 'pw0.chn'), d['chndefs'])

        # TODO handle other parameter types

        if self.hillslope_runs_required:
            self._run_wepp_hillslopes()

        self._run_wepp_watershed()

        return self._load_simulated()

    def _run_wepp_hillslopes(self):
        # TODO: Test this function
        global USE_MULTIPROCESSING
        runs_dir = self.runs_dir

        hillslope_runs = glob(_join(runs_dir, 'p*.run'))
        hillslope_runs = [run for run in hillslope_runs if 'pw' not in run]

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

    def _run_wepp_watershed(self):
        run_watershed(self.runs_dir, self.output_dir)

    def _load_simulated(self):

        # TODO: implement transform from calib
        calib = self.calib

        simulated_d = {}

        for period in calib:
            if period == 'daily':
                simulated_d[period] = {}

                for measure in calib[period]:
                    if measure not in simulated_d:
                        simulated_d[period][measure] = []

                    for obs in calib[period][measure]:
                        _ebe = self._read_ebe()

                        if measure in ['streamflow', 'sediment']:
                            simulated_d[period][measure].append(_ebe.sim_d(measure))
                        else:
                            raise NotImplementedError

            elif period == 'annual':
                raise NotImplementedError
            else:
                raise KeyError

        return simulated_d

    @property
    def first_sim_year(self):
        with open(_join(self.wd, 'wepp', 'runs', 'pw0.cli')) as fp:
            lines = fp.readlines()
            year = int(lines[15].split()[2])

        return year

    def _read_ebe(self):
        ebe_fn = _join(self.output_dir, "ebe_pw0.txt")
        return Ebe(ebe_fn, self.first_sim_year)

    def objectivefunction(self, evaluation, simulation, params=None):
        if simulation is None:
            return 0.0

        simulated_d = simulation
        observed_d = evaluation
        calib = self.calib

        result = 0.0

        like = 0.0

        # loop through the calib and compute objective function
        for period in calib:
            for measure in calib[period]:
                assert period in observed_d
                assert period in simulated_d
                assert measure in observed_d[period]
                assert measure in simulated_d[period]

                for obs_d, sim_d in zip(observed_d[period][measure],
                                             simulated_d[period][measure]):

                    obs_o = obs_d['data']
                    _weight = obs_d['weight']
                    _dates, _obs, _sim = obs_o.build_obs_sim_arrays(sim_d)

                    assert len(_obs) > 0, _obs
                    assert len(_sim) > 0, _sim

                    nse = spotpy.objectivefunctions.nashsutcliffe(_obs, _sim) * _weight
                    if not math.isnan(nse):
                        like += nse

        print(like)
        return like

    def save(self, objectivefunctions, parameter, simulations):
        line=str(objectivefunctions)+','+str(parameter).strip('[]')+','+str(simulations).strip('[]')+'\n'
        self.database.write(line)

if __name__ == '__main__':
    ss = spotpy_setup()
    print(ss.params)
    print(ss.parameters())
    print(ss.parameters())
    print(ss.parameters())
    print(ss.parameters())
    print(ss.parameters())
    print(ss.parameters())
    print(ss.observed_d)
    #vector = ss.parameters()
    #ss.simulation(vector)

ss = spotpy_setup()

sampler = spotpy.algorithms.lhs(ss, dbname='lhs', dbformat='csv', save_sim=False)

rep = 100
sampler.sample(rep)

