import matplotlib.pyplot as pl
import numpy as np
from scipy.integrate import odeint
import time
from scipy.optimize import fmin
import model_new as mod
import time
from joblib import Parallel, delayed
import os

def prepare_folders(data_name):
    save_folder = data_name + "_plots"
    try:
        os.mkdir(save_folder)
    except:
        pass
    save_folder_fit = save_folder + "/data_fit"
    try:
        os.mkdir(save_folder_fit)
    except:
        pass
    save_folder_scores = save_folder + "/data_scores"
    try:
        os.mkdir(save_folder_scores)
    except:
        pass

def plot_data_fit(data, pars_all, pars0, data_name, norm="mean"):
    save_folder = data_name + "_plots/data_fit"
    for i in range(len(data)):
      X0 = mod.get_X0(pars0, pars_all[i]) 
      F = mod.compute_F(pars_all[i], pars0, X0, norm="mean")
      if norm=="mean":
         F_d = data[i]/np.mean(data[i])
      elif norm=="0":
          data = data[i]/data[i][0]
      pl.plot(F, "r")
      pl.plot(F_d, "k")
      pl.savefig(save_folder + "/%s.png"%i, bbox_inches="tight")
      pl.clf()


def plot_scores_params(pars_all, scores, data_name):
   save_folder = data_name + "_plots/data_scores"

   pnames = [r"$\sigma_w$", r"$lhc2_{tot}$",r"$lhcsr_{tot}$", r"init_frac_antenna", "r"]
   snames = [r"$q_T$", r"$q_E$", r"$q_I$"]

   for i in range(len(pars_all[0])):
    for j in range(len(scores[0])):
        X, Y = clip_xy(pars_all[:,i], scores[:,j], mini = 0.015, maxi = 0.985)
        pl.plot(X, Y, "k.")
        pl.xlabel(pnames[i])
        pl.ylabel(snames[j])
        pl.savefig(save_folder + "/%s_p_%s_s_%s.png"%(data_name, i,j))
        pl.clf()

def clip_xy(X,Y, mini = 0.015, maxi = 0.985):
    x_min = np.quantile(X, mini)
    y_min = np.quantile(Y, mini)
    x_max = np.quantile(X, maxi)
    y_max = np.quantile(Y, maxi)
    mask = (X>x_min)*(X<x_max)*(Y>y_min)*(Y<y_max)
    return X[mask], Y[mask]



data_name = "cc124_act"
prepare_folders(data_name)
pars0 = mod.get_pars0()
data = np.loadtxt("estim_params/%s.csv"%data_name, delimiter = ",")
pars_all = np.load("params/params_%s.npy"%data_name)
scores = np.loadtxt("estim_params/%s_scores.csv"%data_name, delimiter=",")

N = pars_all.shape[0]
data = data[:N]
scores = scores[:N]
plot_data_fit(data, pars_all, pars0,  data_name, norm="mean")
plot_scores_params(pars_all, scores, data_name)