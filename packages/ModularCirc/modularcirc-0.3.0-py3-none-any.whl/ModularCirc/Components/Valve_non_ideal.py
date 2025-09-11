from .ComponentBase import ComponentBase
from ..Time import TimeClass
from ..HelperRoutines import non_ideal_diode_flow

import pandas as pd

def gen_q_i_u_func(r, max_func):
    def q_i_u_func(t, y):
        return non_ideal_diode_flow(t, y=y, r=r, max_func=max_func)
    return q_i_u_func

class Valve_non_ideal(ComponentBase):
    def __init__(self,
                 name:str,
                 time_object: TimeClass,
                 r:float,
                 max_func
                 ) -> None:
        super().__init__(name=name, time_object=time_object)
        # allow for pressure gradient but not for flow
        self.make_unique_io_state_variable(q_flag=True, p_flag=False)
        # setting the resistance value
        self.R = r
        self.max_func = max_func

    def q_i_u_func(self, t, y):
        return non_ideal_diode_flow(t, y=y, r=self.R, max_func=self.max_func)

    def setup(self) -> None:
        r        = self.R
        max_func = self.max_func
        # q_i_u_func = lambda t, y: non_ideal_diode_flow(t, y=y, r=r, max_func=max_func)
        q_i_u_func = gen_q_i_u_func(r=r, max_func=max_func)
        self._Q_i.set_u_func(q_i_u_func, function_name='non_ideal_diode_flow + max_func')
        self._Q_i.set_inputs(pd.Series({'p_in':self._P_i.name,
                                        'p_out':self._P_o.name}))
