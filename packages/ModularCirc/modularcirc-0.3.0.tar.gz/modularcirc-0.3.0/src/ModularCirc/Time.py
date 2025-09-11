import numpy as np
import pandas as pd

TEMPLATE_TIME_SETUP_DICT = {
    'name'    :  'generic',
    'ncycles' :  5,
    'tcycle'  :  1.0,
    'dt'      :  0.1,
    'export_min' : 1
 }

class TimeClass():
    def __init__(self, time_setup_dict) -> None:
        self._time_setup_dict = time_setup_dict
        self._initialize_time_array()
        self.cti = 0 # current time step index

    @property
    def ncycles(self):
        if 'ncycles' in self._time_setup_dict.keys():
            return self._time_setup_dict['ncycles']
        else:
            return None

    @property
    def tcycle(self):
        if 'tcycle' in self._time_setup_dict.keys():
            return self._time_setup_dict['tcycle']
        else:
            return None

    @property
    def dt(self):
        if 'dt' in self._time_setup_dict.keys():
            return self._time_setup_dict['dt']
        else:
            return None

    @property
    def export_min(self):
        if 'export_min' in self._time_setup_dict.keys():
            return self._time_setup_dict['export_min']
        else:
            return None

    def _initialize_time_array(self):
        # discretization of on heart beat, used as template
        self._one_cycle_t = pd.Series(np.linspace(
            start= 0.0,
            stop = self.tcycle,
            num  = int(self.tcycle / self.dt)+1,
            dtype= np.float64
            ))

        # discretization of the entire simulation duration
        self._sym_t = pd.Series(
            [t+cycle*self.tcycle for cycle in range(self.ncycles) for t in self._one_cycle_t[:-1]] + [self._one_cycle_t.values[-1]+(self.ncycles-1)*self.tcycle,]
        )

        # array of the current time within the heart cycle
        self._cycle_t = pd.Series(
            [t for _ in range(self.ncycles) for t in self._one_cycle_t[:-1]] + [self._one_cycle_t.values[-1],]
        )

        self.time = pd.DataFrame({'cycle_t' : self._cycle_t, 'sym_t' : self._sym_t})

        # the total number of time steps including initial time step
        self.n_t = len(self._sym_t)

        # the number of time steps in a cycle
        self.n_c = len(self._one_cycle_t)
        return

    def new_time_step(self):
        self.cti += 1
