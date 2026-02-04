import time
import os
import tosacred.SendFit as sf
import tosacred.SendRun as sr
import json
import tools as pt


def send_experiment(data_source, data, res_pars, norm, fit_run='fit', verbose=None):

    # Resolve verbosity: explicit arg wins; else read VERBOSE env
    if verbose is None:
        verbose_env = os.getenv("VERBOSE", "0").lower()
        verbose = verbose_env in ("1", "true", "yes", "on", "debug")

    config = {
        'data_source': data_source,
        'normalization': norm,
    }

    if fit_run == 'fit':
        script = sf
        result_fit, fit_data = res_pars
        config['fit_result'] = pt.fit_result_to_dict(result_fit, verbose=verbose)
    else:
        script = sr
        fit_data, err, result_fit = res_pars
        config['run_result'] = pt.run_result_to_dict(result_fit, err)

    script.shared_data['data'] = data
    script.shared_data['fit_data'] = fit_data

    if verbose:
        print(f"[send_experiment] Mode: {fit_run}")
        try:
            dlen = len(data) if hasattr(data, '__len__') else 'n/a'
            flen = len(fit_data) if hasattr(fit_data, '__len__') else 'n/a'
        except Exception:
            dlen, flen = 'n/a', 'n/a'
        print(f"[send_experiment] data length={dlen}, fit_data length={flen}")
        print(f"[send_experiment] Initial config keys: {list(config.keys())}")

    print("Sending config...")
    memory_file = open('memory.json')
    memory_dict = json.load(memory_file)
    config.update(memory_dict)

    script.ex.add_config(config)

    if verbose:
        print(f"[send_experiment] Merged config keys: {list(config.keys())}")
    print("Config sent.")

    print("Running Exp...")
    t0 = time.time()
    r = script.ex.run()
    dt = time.time() - t0
    if verbose:
        print(f"[send_experiment] Sacred run finished in {dt:.3f}s, id={getattr(r, '_id', None)}")

    latex_img = pt.save_latex_as_image()
    if latex_img is not None:
        tmp_path = pt.save_bytesio_to_tempfile(latex_img)
        r.add_artifact(tmp_path, name="eq_system.png")
        if verbose:
            print("[send_experiment] Attached artifact: eq_system.png")
    r.add_artifact('get_system.py')
    r.add_artifact('memory.json')
    if verbose:
        print("[send_experiment] Attached artifacts: get_system.py, memory.json")

    print(f'Experiment {r._id} has been successfully sent !')
