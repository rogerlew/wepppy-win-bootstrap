from os.path import join as _join
from os.path import split as _split

class PhosphorusOpts(object):
    def __init__(self, surf_runoff=None, lateral_flow=None, baseflow=None, sediment=None):
        # Surface runoff concentration (mg/l)
        self.surf_runoff = surf_runoff

        # Subsurface lateral flow concentration (mg/l)
        self.lateral_flow = lateral_flow

        # Baseflow concentration (mg/l)
        self.baseflow = baseflow

        # Sediment concentration (mg/kg)
        self.sediment = sediment

    def parse_inputs(self, kwds):
        # noinspection PyBroadException
        try:
            self.surf_runoff = float(kwds['surf_runoff'])
            self.lateral_flow = float(kwds['lateral_flow'])
            self.baseflow = float(kwds['baseflow'])
            self.sediment = float(kwds['sediment'])
        except Exception:
            pass

    @property
    def isvalid(self):
        return isfloat(self.surf_runoff) and \
               isfloat(self.lateral_flow) and \
               isfloat(self.baseflow) and \
               isfloat(self.sediment)

    @property
    def contents(self):
        return (
            'Phosphorus concentration\n'
            '{0.surf_runoff}\tSurface runoff concentration (mg/l)\n'
            '{0.lateral_flow}\tSubsurface lateral flow concentration (mg/l)\n'
            '{0.baseflow}\tBaseflow concentration (mg/l)\n'
            '{0.sediment}\tSediment concentration (mg/kg)\n\n'
            .format(self)
        )

    def asdict(self):
        return dict(surf_runoff=self.surf_runoff,
                    lateral_flow=self.lateral_flow,
                    baseflow=self.baseflow,
                    sediment=self.sediment)

def phosphorus_prep(runs_dir, surf_runoff=None, lateral_flow=None, baseflow=None, sediment=None):
    phos_opts = PhosphorusOpts(surf_runoff=surf_runoff, 
                               lateral_flow=lateral_flow, 
                               baseflow=baseflow, 
                               sediment=sediment)
                               
    with open(_join(runs_dir, 'phosphorus.txt'), 'w') as fp:
        fp.write(phos_opts.contents)
    
