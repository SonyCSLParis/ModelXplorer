import numpy as np
import model_new as mn


def get_sys(X, T, pars, pars0):
	L = mn.get_PFD(T, pars0)
	return [ pars0["k_st"]*(pars[0] - X[0]) + X[0]*(L*pars[1] - pars0["k_stn"]), ]


def get_F(sol):
	F = sol[:,0]
	return F
