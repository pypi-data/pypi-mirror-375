import numpy as np
from .Time import TimeClass

import numba as nb

# from numba import jit
from collections.abc import Callable

def resistor_model_flow(t:float,
                        p_in:float=None,
                        p_out:float=None,
                        r:float=None,
                        y:np.ndarray[float]=None
                        ) -> float:
    """
    Resistor model.

    Args:
        p_in (float): input pressure
        p_out (float): ouput pressure
        r (float): resistor constant

    Returns:
        float: q (flow rate through resistive unit)
    """
    if y is not None:
        p_in, p_out= y[:2]
    return (p_in - p_out) / r

def resistor_upstream_pressure(t:float,
                               q_in:float=None,
                               p_out:float=None,
                               r:float=None,
                               y:np.ndarray[float]=None
                               )->float:
    if y is not None:
        q_in, p_out = y[:2]
    return p_out + r * q_in

def resistor_model_dp(q_in:float, r:float) -> float:
    return q_in * r

# @nb.njit(cache=True)
def resistor_impedance_flux_rate(t:float,
                                 p_in:float=None,
                                 p_out:float=None,
                                 q_out:float=None,
                                 r:float=None,
                                 l:float=None,
                                 y:np.ndarray[float]=None) -> float:
    """
    Resistor and impedance in series flux rate of change model.

    Args:
        t (float): current time
        p_in (float): inflow pressure
        p_out (float): outflow pressure
        q_out (float): outflow flux
        r (float): resistor constant
        l (float): impedance constant

    Returns:
        float: flux rate of change
    """
    if y is not None:
        p_in, p_out, q_out = y[:3]
    return (p_in - p_out - q_out * r ) / l

def grounded_capacitor_model_pressure(t:float,
                                      v:float=None,
                                      v_ref:float=None,
                                      c:float=None,
                                      y:np.ndarray[float]=None
                                      ) -> float:
    """
    Capacitor model with constant capacitance.

    Args:
    ----
        v (float): current volume
        v_ref (float): reference volume for which chamber pressure is zero
        c (float): capacitance constant

    Returns:
    --------
        float: pressure at input node
    """
    if y is not None:
        v = y
    return (v - v_ref) / c

def grounded_capacitor_model_volume(t:float,
                                    p:float=None,
                                    v_ref:float=None,
                                    c:float=None,
                                    y:np.ndarray[float]=None
                                    )->float:
    if y is not None:
        p = y
    return v_ref + p * c

# @nb.njit(cache=True)
def grounded_capacitor_model_dpdt(t:float,
                                  q_in:float=None,
                                  q_out:float=None,
                                  c:float=None,
                                  y:np.ndarray[float]=None
                                  ) -> float:
    if y is not None:
        q_in, q_out = y[:2]
    return (q_in - q_out) / c

# @nb.njit(cache=True)
def chamber_volume_rate_change(t:float,
                               q_in:float=None,
                               q_out:float=None,
                               y:np.ndarray[float]=None
                               ) -> float:
    """
    Volume change rate in chamber

    Args:
        q_in (float): _description_
        q_out (float): _description_

    Returns:
        float: _description_
    """
    if y is not None:
        q_in, q_out = y[:2]
    return q_in - q_out

# @nb.njit(cache=True)
def relu_max(val:float) -> float:
    return np.maximum(val, 0.0)

def softplus(val:float, alpha:float=0.2) -> float:
    if isinstance(val, float):
        return 1/ alpha * np.log(1 + np.exp(alpha * val)) if alpha * val <= 20.0 else val
    else:
        y = val.copy()
        y[alpha * y <= 20.0] = 1/ alpha * np.log(1 + np.exp(alpha * y[alpha * y <=20.0]))
        return y

def get_softplus_max(alpha:float):
    """
    Method for generating softmax lambda function based on predefined alpha values

    Args:
    ----
        alpha (float): softplus alpha value

    Returns:
    -------
        function: softplus function with fixed alpha
    """
    return lambda val : softplus(val=val, alpha=alpha)

def non_ideal_diode_flow(t:float,
                         p_in:float=None,
                         p_out:float=None,
                         r:float=None,
                         max_func:Callable[[float],float]=relu_max,
                         y:np.ndarray[float]=None,
                         ) -> float:
    """
    Non-ideal diode model with the option to choose the re

    Args:
    -----
        p_in (float): input pressure
        p_out (float): output pressure
        r (float): valve constant resistance
        max_func (function): function that dictates when valve opens

    Returns:
        float: q (flow rate through valve)
    """
    if y is not None:
        p_in, p_out = y[:2]
    return (max_func((p_in - p_out)/ r))

# @jit(cache=True, nopython=True)
def simple_bernoulli_diode_flow(t:float,
                         p_in:float=None,
                         p_out:float=None,
                         CQ:float=None,
                         RRA:float=0.0,
                         y:np.ndarray[float]=None,
                         ) -> float:
    """
    Non-ideal diode model with the option to choose the re

    Args:
    -----
        p_in (float): input pressure
        p_out (float): output pressure
        r (float): valve constant resistance
        max_func (function): function that dictates when valve oppens

    Returns:
        float: q (flow rate through valve)
    """
    if y is not None:
        p_in, p_out = y[:2]
    dp   = p_in - p_out
    return np.where(dp >= 0.0,
                    CQ * np.sqrt(np.abs(dp)),
                   -CQ * RRA *np.sqrt(np.abs(dp)))

# @jit(cache=True, nopython=True)
def maynard_valve_flow(t:float,
                       p_in:np.ndarray[float]=None,
                       p_out:np.ndarray[float]=None,
                       phi:np.ndarray[float]=None,
                       CQ:float=None,
                       RRA:float=0.0,
                       y:np.ndarray[float]=None
                       )->np.ndarray[float]:
    if y is not None:
        p_in, p_out, phi = y[:3]
    dp = p_in - p_out
    aeff = (1.0 - RRA) * phi + RRA
    return np.where(dp >= 0.0, aeff, -aeff) * CQ * np.sqrt(np.abs(dp))

# @nb.njit(cache=True,)
def maynard_phi_law(t:float,
                    p_in:nb.types.Array =None,
                    p_out:nb.types.Array=None,
                    phi:nb.types.Array  =None,
                    Ko:float            =None,
                    Kc:float            =None,
                    y:nb.types.Array    =None
                    )->nb.types.Array:
    if y is not None:
        p_in, p_out, phi = y[:3]
    dp = p_in - p_out
    return np.where(dp >= 0.0, Ko * (1.0 - phi) * dp, Kc * phi * dp)

# @nb.njit(cache=True)
def maynard_impedance_dqdt(t:float,
                           p_in:nb.types.Array =None,
                           p_out:nb.types.Array =None,
                           q_in:nb.types.Array =None,
                           phi:nb.types.Array =None,
                           CQ:float=None,
                           R :float=None,
                           L :float=None,
                           RRA:float=0.0,
                           y:nb.types.Array =None
                           )->nb.types.Array:
    if y is not None:
        p_in, p_out, q_in, phi = y[:4]
    dp   = p_in - p_out
    aeff = (1.0 - RRA) * phi + RRA
    return np.where(aeff > 1.0e-5, (dp * aeff - q_in * R * aeff  - q_in * np.abs(q_in) / CQ**2.0 * aeff**(-1.0)  ) / L, 0.0)

def leaky_diode_flow(p_in:float, p_out:float, r_o:float, r_r:float) -> float:
    """
    Leaky diode model that outputs the flow rate through a leaky diode

    Args:
        p_in (float): input pressure
        p_out (float): output pressure
        r_o (float): outflow resistance
        r_r (float): regurgitant flow resistance

    Returns:
        float: q flow rate through diode
    """
    dp = p_in - p_out
    return np.where(dp >= 0.0, dp/r_o, dp/r_r)

def activation_function_1(t:float, t_max:float, t_tr:float, tau:float, dt: bool=False) -> float:
    """
    Activation function that dictates the transition between the passive and active behaviors.
    Based on the definition used in Naghavi et al (2024).

    Args:
        t (float):     current time within the cardiac cycle
        t_max (float): time to peak tension
        t_tr (float):  transition time
        tau (float):   the relaxation time constant

    Returns:
        float: activation function value
    """
    if not dt:
        if t <= t_tr:
            return 0.5 * (1.0 - np.cos(np.pi * t / t_max))
        else:
            coeff = 0.5 * (1.0 - np.cos(np.pi * t_tr / t_max))
            return  np.exp(-(t - t_tr)/tau) * coeff
    else:
        if t <= t_tr:
            return 0.5 * np.pi / t_max * np.sin(np.pi * t / t_max)
        else:
            coeff = 0.5 * (1.0 - np.cos(np.pi * t_tr / t_max))
            return - np.exp(-(t - t_tr)/tau) * coeff / tau

def activation_function_2(t:float, tr:float, td:float, dt: bool=True) -> float:
    if not dt:
        result = (
            0.5 * (1.0 - np.cos(np.pi * t / tr)) if t < tr else
            0.5 * (1.0 + np.cos(np.pi * (t - tr) / (td - tr))) if t < td else
            0.0
        )
    else:
        result = (
            0.5 * np.pi / tr * np.sin(np.pi * t / tr) if t < tr else
           -0.5 * np.pi /(td - tr) * np.sin(np.pi * (t - tr) / (td - tr)) if t < td else
            0.0
        )
    return result

def activation_function_3(t:float, tpwb:float, tpww:float, dt: bool=True) -> float:
    if not dt:
        result = (
            0.0 if t < tpwb else
            0.5 * (1 - np.cos(2.0 * np.pi * (t - tpwb) / tpww)) if t < tpwb + tpww else
            0.0
        )
    else:
        result = (
            0.0 if t < tpwb else
            np.pi /tpww * np.sin(2.0 * np.pi * (t - tpwb) / tpww) if t < tpwb + tpww else
            0.0
        )
    return result

def activation_function_4(t:float, t_max:float, t_tr:float, tau:float, dt: bool=True) -> float:
    """
    Activation function that dictates the transition between the passive and active behaviors.
    Based on the definition used in Naghavi et al (2024).

    Args:
        t (float):     current time within the cardiac cycle
        t_max (float): time to peak tension
        t_tr (float):  transition time
        tau (float):   the relaxation time constant

    Returns:
        float: activation function value
    """
    if not dt:
        return (
            0.5 * (1.0 - np.cos(np.pi * t / t_max)) if 0 <= t <= t_tr else
            np.exp(-(t - t_tr) / tau) if t >= 0 else
            0.0
        )
    else:
        return (
            0.5 * np.sin(np.pi * t / t_max) / t_max if 0 <= t <= t_tr else
            - np.exp(-(t - t_tr) / tau) / tau if t >= 0 else
            0.0
        )

def chamber_linear_elastic_law(v:float, E:float, v_ref:float, *args, **kwargs) -> float:
    """
    Linear elastance model

    Args:
        v (float): volume
        E (float): Elastance
        v_ref (float): reference volume

    Returns:
        float: chamber pressure
    """
    return E * (v - v_ref)

def chamber_exponential_law(v:float, E:float, k:float, v_ref:float, *args, **kwargs) -> float:
    """
    Exponential chamber law

    Args:
        v (float): volume
        E (float): elastance constant
        k (float): exponential factor
        v_ref (float): reference volume

    Returns:
        float: chamber pressure
    """
    return E * np.exp(k * (v - v_ref) - 1)

def chamber_pressure_function(t:float, v:float, v_ref:float, E_pas:float, E_act:float,
                              activation_function = activation_function_1,
                              active_law = chamber_linear_elastic_law,
                              passive_law = chamber_linear_elastic_law,
                              *args, **kwargs) ->float:
    """
    Generic function returning the chamber pressure at a given time for a given imput

    Args:
    -----
        t (float): current time
        v (float): current volume
        v_ref (float) : reference volume
        activation_function (procedure): activation function
        active_law (procedure): active p-v relation
        passive_law (procedure): passive p-v relation

    Returns:
    --------
        float: pressure
    """
    a = activation_function(t)
    return (a * active_law(v=v, v_ref=v_ref,t=t, E=E_act, **kwargs)
            + (1 - a) * passive_law(v=v, v_ref=v_ref, t=t, E=E_pas, **kwargs))

def time_shift(t:float, shift:float=np.nan, tcycle:float=0.0):
    if shift is np.nan:
        return t
    elif t < tcycle - shift:
        return t + shift
    else:
        return t + shift - tcycle


BOLD = '\033[1m'
YELLOW = '\033[93m'
END  = '\033[0m'

def bold_text(str_:str):
    return BOLD + YELLOW + str_ + END
