import numpy as np
import get_system as gs
import json
from scipy.integrate import odeint
import tools as pt
import os
from scipy.optimize import fsolve


def get_PFD(T, pars0):
    return ((T < pars0['stim']["PFDTs"][0])+(T > pars0['stim']["PFDTs"][1]))*pars0['PFD']['dark']+pars0['PFD']['light']*((T > pars0['stim']["PFDTs"][0])*(T < pars0['stim']["PFDTs"][1]))


def get_sys(X, T, pars, pars0): 
    return gs.get_sys(X, T, pars, pars0)


def get_F(sol):
   return gs.get_F(sol)


def get_X0(pars0, pars):
    def initial_eq(X):
        return gs.get_sys(X, 0, pars, pars0)
    
    return fsolve(initial_eq, np.array([0.5]*pt.get_sys_dimension()))


def compute_F(pars, pars0, X0, len_data, h=0.007, norm=None):
    N = np.sum(pars0['stim']['PFDTs'])
    t = np.linspace(0, N, int(N/h))
    sol = odeint(get_sys, X0, t, args=(pars, pars0), hmax=h, mxstep=500)

    F = get_F(sol)
    F = F[::2500]

    cut = (len_data + 5) - len(F)

    F = F[5:cut]

    F = pt.normalize_data(F, norm)

    if norm == "mean":
       F = F/np.mean(F)
    elif norm == "0":
       F = F/F[45]
    return F


def get_pars0(memory_file = "memory.json"):
    with open(memory_file, "r") as m:
        memory = json.load(m)

    pars0 = memory['fixed_params']

    pars0['PFD'] = memory['pfd_params']

    pars0['stim'] = {
        'PFDTs': memory['pfd_params']['PFDTs'],
        'PFDamp': [pars0['PFD']['dark'], pars0['PFD']['light'], pars0['PFD']['dark']]
    }

    pars0["lhc2_init"] = 0.7
    pars0["lhcsr_init"] = 0.7

    return pars0


def get_pars(memory_file = "memory.json"):
    with open(memory_file, "r") as m:
        memory = json.load(m)

    pars_dict = memory['variable_params']

    sorted_pars = dict(sorted(pars_dict.items()))
    pars = []

    for p in sorted_pars:
        pars.append(sorted_pars[p])

    return pars
