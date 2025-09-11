from .OdeModel import OdeModel
from .NaghaviModelParameters import NaghaviModelParameters, TEMPLATE_TIME_SETUP_DICT
from ..Components import Rlc_component, Valve_non_ideal, HC_mixed_elastance
from ..HelperRoutines import *

class NaghaviModel(OdeModel):
    def __init__(self, time_setup_dict, parobj:NaghaviModelParameters=NaghaviModelParameters(), suppress_printing:bool=False) -> None:
        super().__init__(time_setup_dict)
        self.name = 'NaghaviModel'

        if not suppress_printing: print(parobj)

        # Defining the aorta object
        self.components['ao'] = Rlc_component( name='Aorta',
                                time_object=self.time_object,
                                r     = parobj['ao']['r'],
                                c     = parobj['ao']['c'],
                                l     = parobj['ao']['l'],
                                v_ref = parobj['ao']['v_ref'],
                                v     = parobj['ao']['v'],
                                  )
        self.set_v_sv('ao')

        # Defining the arterial system object
        self.components['art'] = Rlc_component(name='Arteries',
                                time_object=self.time_object,
                                r     = parobj['art']['r'],
                                c     = parobj['art']['c'],
                                l     = parobj['art']['l'],
                                v_ref = parobj['art']['v_ref'],
                                v     = parobj['art']['v'],
                                )
        self.set_v_sv('art')

        # Defining the venous system object
        self.components['ven'] = Rlc_component(name='VenaCava',
                                time_object=self.time_object,
                                r     = parobj['ven']['r'],
                                c     = parobj['ven']['c'],
                                l     = parobj['ven']['l'],
                                v_ref = parobj['ven']['v_ref'],
                                v     = parobj['ven']['v'],
                                )
        self.set_v_sv('ven')

        # Defining the aortic valve object
        self.components['av']  = Valve_non_ideal(name='AorticValve',
                                     time_object=self.time_object,
                                     r=parobj['av']['r'],
                                     max_func=parobj['av']['max_func']
                                     )

        # Defining the mitral valve object
        self.components['mv'] = Valve_non_ideal(name='MitralValve',
                                    time_object=self.time_object,
                                    r=parobj['mv']['r'],
                                    max_func=parobj['mv']['max_func']
                                    )

        # Defining the left atrium activation function
        # def la_af(t, t_max=parobj['la']['t_max'], t_tr=parobj['la']['t_tr'], tau=parobj['la']['tau'], af=parobj['la']['activation_function']):
        #     return af(time_shift(t, 100., self.time_object), t_max=t_max, t_tr=t_tr, tau=tau)
        # Defining the left atrium class
        self.components['la'] = HC_mixed_elastance(name='LeftAtrium',
                                        time_object=self.time_object,
                                        E_pas=parobj['la']['E_pas'],
                                        E_act=parobj['la']['E_act'],
                                        v_ref=parobj['la']['v_ref'],
                                        k_pas=parobj['la']['k_pas'],
                                        v    =parobj['la']['v'],
                                        af   =parobj['la']['activation_function'],
                                        t_tr =parobj['la']['t_tr'],
                                        t_max=parobj['la']['t_max'],
                                        tau  =parobj['la']['tau'],
                                        delay=parobj['la']['delay']
                                        )
        self._state_variable_dict['v_la'] = self.components['la']._V
        self._state_variable_dict['v_la'].set_name('v_la')
        self.all_sv_data['v_la'] = self.components['la'].V
        self.components['la']._V._u = self.all_sv_data['v_la']

        # Defining the left ventricle activation function
        self.components['lv'] = HC_mixed_elastance(name='LeftVentricle',
                                        time_object=self.time_object,
                                        E_pas=parobj['lv']['E_pas'],
                                        E_act=parobj['lv']['E_act'],
                                        k_pas=parobj['lv']['k_pas'],
                                        v_ref=parobj['lv']['v_ref'],
                                        v    =parobj['lv']['v'],
                                        af   =parobj['lv']['activation_function'],
                                        t_tr =parobj['la']['t_tr'],
                                        t_max=parobj['la']['t_max'],
                                        tau  =parobj['la']['tau'],
                                        delay=parobj['lv']['delay']
                                        )
        self._state_variable_dict['v_lv'] = self.components['lv']._V
        self._state_variable_dict['v_lv'].set_name('v_lv')
        self.all_sv_data['v_lv'] = self.components['lv'].V
        self.components['lv']._V._u = self.all_sv_data['v_lv']

        for component in self.components.values():
            component.setup()

        # connect the left ventricle class to the aortic valve
        self.connect_modules(self.components['lv'],
                             self.components['av'],
                             plabel='p_lv',
                             qlabel='q_av',
                             )
        # connect the aortic valve to the aorta
        self.connect_modules(self.components['av'],
                             self.components['ao'],
                             plabel='p_ao',
                             qlabel='q_av')
        # connect the aorta to the arteries
        self.connect_modules(self.components['ao'],
                             self.components['art'],
                             plabel= 'p_art',
                             qlabel= 'q_ao')
        # connect the arteries to the veins
        self.connect_modules(self.components['art'],
                             self.components['ven'],
                             plabel= 'p_ven',
                             qlabel= 'q_art')
        # connect the veins to the left atrium
        self.connect_modules(self.components['ven'],
                             self.components['la'],
                             plabel= 'p_la',
                             qlabel='q_ven',
                             )
        # connect the left atrium to the mitral valve
        self.connect_modules(self.components['la'],
                             self.components['mv'],
                             plabel= 'p_la',
                             qlabel='q_mv')
        # connect the mitral valve to the left ventricle
        self.connect_modules(self.components['mv'],
                             self.components['lv'],
                             plabel='p_lv',
                             qlabel='q_mv',
                             )

        for component in self.components.values():
            component.setup()
