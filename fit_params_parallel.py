import matplotlib.pyplot as pl
import numpy as np
import time
import random
import os
from scipy.optimize import fmin
#from current_model import get_sys, pars, pars0, X0
import model_new as mod
import time
import multiprocessing
from joblib import Parallel, delayed
import ipdb
import tools as pt


def _verbose():
    return os.getenv('FIT_VERBOSE', '1') not in ('0', 'false', 'False')


def _log(msg):
    if _verbose():
        print(f"[Fit] {msg}", flush=True)


def _get_int_env(name, default):
    try:
        v = os.getenv(name)
        if v is None or v == '':
            return default
        return int(v)
    except Exception:
        return default


def get_error(pars, data, pars0, norm=None, queue=None):

    X0 = mod.get_X0(pars0, pars)

    F = mod.compute_F(pars, pars0, X0, len(data), norm=norm)

    err = np.mean((F - data)**2)
    if not np.isfinite(err):
        _log("Non-finite error encountered; returning large penalty.")
        err = 1e12

    if queue is not None:
        queue.put(F.tolist())

    return err


def get_Ferr(pars, data, pars0, norm=None, queue=None):
    X0 = mod.get_X0(pars0, pars)

    F = mod.compute_F(pars, pars0, X0, len(data), norm=norm)

    err = np.mean((F - data)**2)

    if queue is not None:
        queue.put(F.tolist())

    return F, err, X0


def get_pars(data, pars, pars0, i, N, queue, norm=None):
    if norm is None:
        norm = {"type": "div", "val": "mean"}
    # Avoid division by zero in logs if N is not provided
    total = N if (isinstance(N, int) and N > 0) else 1
    _log(f"Trace {i+1}/{total} start | len(data)={len(data)} | norm={norm}")
    _log(f"Initial pars: {np.array2string(np.array(pars), precision=4, separator=', ')}")
    t0 = time.time()
    # Initial error for diagnostics
    try:
        init_err = get_error(pars, data, pars0, norm, None)
        _log(f"Initial MSE: {init_err:.6g}")
    except Exception as e:
        _log(f"Failed to compute initial error: {e}")
    maxiter = _get_int_env('FIT_MAXITER', 1000)
    maxfun = _get_int_env('FIT_MAXFUN', 2000)
    disp = os.getenv('FIT_FMIN_DISP', '1') not in ('0', 'false', 'False')
    _log(f"Starting optimizer (maxiter={maxiter}, maxfun={maxfun})")
    try:
        _log("Entering optimizer (scipy.optimize.fmin)")
        try:
            dlen = len(data)
        except Exception:
            dlen = 'n/a'
        _log(f"fmin args summary | len(data)={dlen} | pars_len={len(pars)} | disp={disp} | maxiter={maxiter} | maxfun={maxfun}")
        res = fmin(
            get_error,
            pars,
            args=(data, pars0, norm, queue),
            full_output=True,
            disp=disp,
            maxiter=maxiter,
            maxfun=maxfun,
        )
        _log("fmin returned successfully")
    except Exception as e:
        _log(f"Optimizer failed with error: {e}")
        raise
    dt = time.time() - t0
    try:
        xopt, fopt, iters, funcalls, warnflag = res[:5]
        _log(f"Done trace {i+1}/{total} | MSE={fopt:.6g} | iters={iters} | evals={funcalls} | warn={warnflag} | dt={dt:.3f}s")
        _log(f"Best pars: {np.array2string(np.array(xopt), precision=5, separator=', ')}")
        if warnflag != 0:
            _log("Optimizer issued a warning (likely max iter/evals reached)")
        done_info = {"_done": True, "iters": int(iters), "evals": int(funcalls), "fopt": float(fopt)}
    except Exception:
        _log(f"Done trace {i+1}/{total} in {dt:.3f}s")
        done_info = {"_done": True}
    F, err, X0 = get_Ferr(res[0], data, pars0, norm)
    # Signal completion to any listener (e.g., UI) via queue sentinel
    try:
        if queue is not None:
            queue.put(done_info)
    except Exception:
        pass
    return res, F


def parallel_params(data, pars, pars0):
    N = data.shape[0]
    t0 = time.time()
    res = Parallel(n_jobs=38)(delayed(get_pars)(data[i], pars, pars0, i, N) for i in range(N))
    ps = np.array([r[0] for r in res])
    rs = np.array([r[1] for r in res])
    print("it took ", time.time()-t0, "s")
    return ps, rs
