import spotpy
import numpy as np

import os

from os.path import join as _join
from os.path import split as _split
from os.path import exists
import json
from glob import glob
import multiprocessing

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
    wait,
    FIRST_EXCEPTION
)

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

USE_MULTIPROCESSING = True

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
        """
        TODO for next time. The first time this runs vector is a list of tuples. The second time it is some sort of
        parameters object and the __iter__ returns scalar values.


        C:\Python38\python.exe C:/Users/roger/Documents/GitHub/wepppy-win-bootstrap/scripts/spotpy_setup.py
wd C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast
[Uniform('chndefs:chnk', [1e-08, 1.0]), Uniform('chndefs:chntcr', [0.0, 100.0]), Uniform('chndefs:chnedm', [0.01, 1.5]), Uniform('chndefs:chneds', [0.01, 1.5])]
[( 0.58271538, 'chndefs:chnk',  0.0939,   0.20854, 0.000467,  0.997, False)
 (71.27357704, 'chndefs:chntcr', 10.5   , 100.     , 0.0706  , 99.6  , False)
 ( 0.64233109, 'chndefs:chnedm',  0.154 ,   0.5    , 0.0114  ,  1.5  , False)
 ( 1.41939844, 'chndefs:chneds',  0.123 ,   0.1    , 0.0105  ,  1.5  , False)]
[( 0.59594868, 'chndefs:chnk',  0.0939,   0.20854, 0.000467,  0.997, False)
 (86.13313955, 'chndefs:chntcr', 10.5   , 100.     , 0.0706  , 99.6  , False)
 ( 0.60201818, 'chndefs:chnedm',  0.154 ,   0.5    , 0.0114  ,  1.5  , False)
 ( 0.60853516, 'chndefs:chneds',  0.123 ,   0.1    , 0.0105  ,  1.5  , False)]
[( 0.98881328, 'chndefs:chnk',  0.0939,   0.20854, 0.000467,  0.997, False)
 (77.89511292, 'chndefs:chntcr', 10.5   , 100.     , 0.0706  , 99.6  , False)
 ( 0.21661722, 'chndefs:chnedm',  0.154 ,   0.5    , 0.0114  ,  1.5  , False)
 ( 0.67918024, 'chndefs:chneds',  0.123 ,   0.1    , 0.0105  ,  1.5  , False)]
[( 0.5120639 , 'chndefs:chnk',  0.0939,   0.20854, 0.000467,  0.997, False)
 (66.88963142, 'chndefs:chntcr', 10.5   , 100.     , 0.0706  , 99.6  , False)
 ( 0.88528599, 'chndefs:chnedm',  0.154 ,   0.5    , 0.0114  ,  1.5  , False)
 ( 0.60231921, 'chndefs:chneds',  0.123 ,   0.1    , 0.0105  ,  1.5  , False)]
[( 0.88184448, 'chndefs:chnk',  0.0939,   0.20854, 0.000467,  0.997, False)
 (80.10379312, 'chndefs:chntcr', 10.5   , 100.     , 0.0706  , 99.6  , False)
 ( 1.2328678 , 'chndefs:chnedm',  0.154 ,   0.5    , 0.0114  ,  1.5  , False)
 ( 0.84328984, 'chndefs:chneds',  0.123 ,   0.1    , 0.0105  ,  1.5  , False)]
[( 0.10292037, 'chndefs:chnk',  0.0939,   0.20854, 0.000467,  0.997, False)
 (71.34160102, 'chndefs:chntcr', 10.5   , 100.     , 0.0706  , 99.6  , False)
 ( 1.48640569, 'chndefs:chnedm',  0.154 ,   0.5    , 0.0114  ,  1.5  , False)
 ( 0.73182494, 'chndefs:chneds',  0.123 ,   0.1    , 0.0105  ,  1.5  , False)]
{'daily': {'sediment': [{'path': 'C:\\Users\\roger\\Documents\\GitHub\\wepppy-win-bootstrap-mica-test-run\\clear-cut-blast\\observed\\Mica_fl3_daily_observed_sediment.csv', 'weight': 0.25, 'data': <observed.DailyObserved object at 0x0000025B869BBBB0>}, {'path': 'C:\\Users\\roger\\Documents\\GitHub\\wepppy-win-bootstrap-mica-test-run\\clear-cut-blast\\observed\\Mica_fl3_daily_observed_sediment.csv', 'weight': 0.25, 'data': <observed.DailyObserved object at 0x0000025B869BBBE0>}], 'streamflow': [{'path': 'C:\\Users\\roger\\Documents\\GitHub\\wepppy-win-bootstrap-mica-test-run\\clear-cut-blast\\observed\\Mica_fl3_daily_observed_sediment.csv', 'weight': 0.5, 'transform': 'log', 'data': <observed.DailyObserved object at 0x0000025B822812E0>}]}}
vector [( 0.67094222, 'chndefs:chnk',  0.0939,   0.20854, 0.000467,  0.997, False)
 (40.96958331, 'chndefs:chntcr', 10.5   , 100.     , 0.0706  , 99.6  , False)
 ( 0.93503375, 'chndefs:chnedm',  0.154 ,   0.5    , 0.0114  ,  1.5  , False)
 ( 1.18296914, 'chndefs:chneds',  0.123 ,   0.1    , 0.0105  ,  1.5  , False)]
thing 0 (0.67094222, 'chndefs:chnk', 0.0939, 0.20854, 0.000467, 0.997, False)
thing 1 (40.96958331, 'chndefs:chntcr', 10.5, 100., 0.0706, 99.6, False)
thing 2 (0.93503375, 'chndefs:chnedm', 0.154, 0.5, 0.0114, 1.5, False)
thing 3 (1.18296914, 'chndefs:chneds', 0.123, 0.1, 0.0105, 1.5, False)
guesses {'chnk': 0.6709422249058248, 'chntcr': 40.969583313463495, 'chnedm': 0.9350337527112201, 'chneds': 1.1829691428041644, 'chnz': 19.99, 'chnnbr': 0.04, 'chnn': 0.3, 'ctlslp': 0.02, 'ctlz': 4.0, 'ctln': 0.04}
runs_dir C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast\wepp/runs
wd C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast
Initializing the  Shuffled Complex Evolution (SCE-UA) algorithm  with  2  repetitions
The objective function will be minimized
Starting burn-in sampling...
Exception in thread Thread-1:
Traceback (most recent call last):
  File "C:\Python38\lib\threading.py", line 932, in _bootstrap_inner
    self.run()
  File "C:\Python38\lib\threading.py", line 870, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Python38\lib\site-packages\spotpy\algorithms\_algorithm.py", line 438, in model_layer
    q.put(self.setup.simulation(self.partype(*all_params)))
  File "C:/Users/roger/Documents/GitHub/wepppy-win-bootstrap/scripts/spotpy_setup.py", line 116, in simulation
    val = tup[0]
IndexError: invalid index to scalar variable.
Traceback (most recent call last):
  File "C:\Python38\lib\site-packages\spotpy\algorithms\_algorithm.py", line 420, in getfitness
    return self.setup.objectivefunction(evaluation=self.evaluation, simulation=simulation, params = (params,self.parnames))
  File "C:/Users/roger/Documents/GitHub/wepppy-win-bootstrap/scripts/spotpy_setup.py", line 215, in objectivefunction
    assert period in simulated_d
TypeError: argument of type 'NoneType' is not iterable

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:/Users/roger/Documents/GitHub/wepppy-win-bootstrap/scripts/spotpy_setup.py", line 244, in <module>
    sampler.sample(2)
  File "C:\Python38\lib\site-packages\spotpy\algorithms\sceua.py", line 186, in sample
    like = self.postprocessing(icall, randompar, simulations,chains=0)
  File "C:\Python38\lib\site-packages\spotpy\algorithms\_algorithm.py", line 398, in postprocessing
    like = self.getfitness(simulation=simulation, params=params)
  File "C:\Python38\lib\site-packages\spotpy\algorithms\_algorithm.py", line 424, in getfitness
    return self.setup.objectivefunction(evaluation=self.evaluation, simulation=simulation)
  File "C:/Users/roger/Documents/GitHub/wepppy-win-bootstrap/scripts/spotpy_setup.py", line 215, in objectivefunction
    assert period in simulated_d
TypeError: argument of type 'NoneType' is not iterable
vector parameters(chndefs:chnk=0.818108, chndefs:chntcr=95.7634, chndefs:chnedm=0.448778, chndefs:chneds=0.207952)
thing 0 0.8181078351558362
thing 1 95.76336022817348
thing 2 0.4487778677482809
thing 3 0.20795150378321828

Process finished with exit code 1
        """
        print('vector', vector)

        for i, thing in enumerate(vector):
            print('thing', i, thing)

        d = {}


        for tup in vector:
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

    def _read_ebe(self):
        ebe_fn = _join(self.output_dir, "ebe_pw0.txt")
        return Ebe(ebe_fn)

    def objectivefunction(self, evaluation, simulation, params=None):
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

                for _obs_instance in observed_d[period][measure]: # e.g. DailyObserved
                    _dates, _obs, _sim = _obs_instance.build_obs_sim_arrays(simulated_d[period][measure])
                    _weight = calib[period][measure]['weight']
                    like += spotpy.objectivefunctions.nashsutcliffe(_obs, _sim) * _weight
        return like


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
    vector = ss.parameters()
    ss.simulation(vector)


sampler = spotpy.algorithms.sceua(
    spotpy_setup(used_algorithm='sceua'),
    dbname='SCEUA_CMF', dbformat='csv')

sampler.sample(2)
print(sampler.getdata)