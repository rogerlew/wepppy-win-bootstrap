from os.path import exists
from datetime import datetime

import csv


def isfloat(x):
    try:
        float(x)
    except:
        return False

    return True


class DailyObserved(object):
    def __init__(self, fn):
        assert exists(fn)

        fp = open(fn)

        rdr = csv.DictReader(fp)

        assert 'Date' in rdr.fieldnames
        assert len(rdr.fieldnames) == 2
        key = set(rdr.fieldnames).difference(['Date']).pop()

        d = {}
        for row in rdr:
            _date = datetime.strptime(row['Date'], '%m/%d/%Y')
            assert _date not in d

            value = row[key]
            if value != '-9999':
                if isfloat(value):
                    d[(_date.year, _date.month, _date.day)] = float(value)

        fp.close()

        self.key = key
        self.data = d

    def build_obs_sim_arrays(self, sim_d):
        obs_d = self.data

        dates = []
        obs = []
        sim = []

        for key in sim_d:
            if key in obs_d:
                obs.append(obs_d[key])
                sim.append(sim_d[key])
                dates.append(key)

        return dates, obs, sim


if __name__ == "__main__":
    from pprint import pprint

    fn1 = r"C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast\observed\Mica_fl3_daily_observed_sediment.csv"
    daily_sed_obs = DailyObserved(fn1)

    pprint(daily_sed_obs.data)

    fn2 = r"C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast\observed\Mica_fl3_daily_observed_streamflow.csv"
    daily_streamflow_obs = DailyObserved(fn2)

    pprint(daily_streamflow_obs.data)

    chanwb_fn = r"C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast\wepp\output\chanwb.out"

    from wepp.out import Chanwb
    from wepp.out import Loss
    loss_fn = r"C:\Users\roger\Documents\GitHub\wepppy-win-bootstrap-mica-test-run\clear-cut-blast\wepp\output\loss_pw0.txt"
    loss = Loss(loss_fn)
    wsarea = loss.wsarea
    print('wsarea', wsarea)

    chanwb = Chanwb(chanwb_fn)
    sim_outflow_d = chanwb.outflow

    pprint(sim_outflow_d)

    dates, obs_outflow, sim_outflow = daily_streamflow_obs.build_obs_sim_arrays(sim_outflow_d)

    for _date, obs, sim in zip(dates, obs_outflow, sim_outflow):
        print(_date, obs, sim)



