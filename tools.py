import json
import os
import re
import time
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ast
import sympy as sp
import io
import tempfile
import subprocess
from pdf2image import convert_from_path
from sympy.parsing.sympy_parser import parse_expr


def convert_to_float(val):
    if isinstance(val, str):
        try:
            if '/' in val:
                numerator, denominator = val.split('/')
                return float(numerator) / float(denominator)

            elif ',' in val:
                val.replace(' ', '')
                values = val.split(',')
                array = []

                for v in values:
                    array.append(float(v))

                return array

            else:
                return float(val)

        except (ValueError, ZeroDivisionError):
            return val
    else:
        return val


def get_data(stored_data):
    data_params = pd.DataFrame(stored_data)
    data_params = data_params[['run_id', 'algae']]
    data_metrics = pd.read_csv("dataset/metrics_npq_score.csv")
    filtered_metrics = data_metrics.merge(data_params, on=['run_id', 'algae'], how='inner')
    rd_line_vals = filtered_metrics.drop(columns=['run_id', 'algae'])
    data = rd_line_vals.iloc[0].to_numpy()

    return data


def detect_variables(text_equation):
    text_equation = text_equation.replace(' ', '')
    text_equation = text_equation.replace('$', 'var_')
    # text_equation = text_equation.replace('\n', '')
    text_equation = text_equation.replace('np', 'sympy')
    eq_txt_list = text_equation.split('\n')

    eq_dict = {}
    eq_list = []

    for eq in eq_txt_list:
        elem = eq.split("=")
        eq_dict[elem[0]] = elem[1]
        eq_list.append(elem[1])

    var_list = []

    for eq in eq_list:
        expression = sp.sympify(eq)
        variables = [str(var) for var in expression.free_symbols]
        var_list += variables

    return var_list


def get_params(text_equation):
    var_list = detect_variables(text_equation)

    fixed_par_list = []
    variable_par_list = []

    for var in var_list:
        if var not in variable_par_list and var not in fixed_par_list:
            if not ('X' in var and len(var) == 2 or var == 'PFD' or var == 'L'):
                if 'var_' in var:
                    var = var.replace('var_', '')
                    variable_par_list.append(var)
                else:
                    fixed_par_list.append(var)

    fixed_par_list.sort()
    variable_par_list.sort()

    return fixed_par_list, variable_par_list


def get_system(text_equation):

    with open("memory.json", "r") as m:
        memory = json.load(m)
        f_pars = memory.get('fixed_params', {})
        v_pars = memory.get('variable_params', {})

    v_pars_list = list(v_pars.keys())

    new_text_equation = text_equation

    for par in f_pars:
        new_text_equation = re.sub(rf'\b{re.escape(par)}\b', f'pars0["{par}"]', new_text_equation)

    for i in range(len(v_pars)):
        new_text_equation = re.sub(rf'\b{re.escape(v_pars_list[i])}\b', f'pars[{i}]', new_text_equation).replace('$', '')

    eq_txt_list = new_text_equation.split('\n')

    eq_dict = {}

    for eq in eq_txt_list:
        elem = eq.split("=")
        equation = elem[1]
        equation = equation.replace(f'exp', f'np.exp')

        for i in range(len(eq_txt_list)):
            equation = equation.replace(f'X{i}', f'X[{i}]')

        eq_dict[elem[0].replace(' ', '')] = equation

    return eq_dict


def _write_atomic(filepath: str, content: str):
    """Write content atomically, replacing the target file.
    This avoids permission issues from unlinking in some environments.
    """
    dirpath = os.path.dirname(os.path.abspath(filepath)) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".tmp_get_system_", dir=dirpath)
    try:
        with os.fdopen(fd, "w") as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
        # Replace is atomic on POSIX; on Windows it will overwrite if possible
        os.replace(tmp_path, filepath)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


def generate_py_file(system_text, fluo_eq):
    eq_dict = get_system(system_text)

    imports = ("import numpy as np\n"
               "import model_new as mn\n\n\n")

    get_sys = ("def get_sys(X, T, pars, pars0):\n"
               "\tL = mn.get_PFD(T, pars0)\n"
               "\treturn [")

    for eq in eq_dict:
        get_sys = get_sys + eq_dict[eq] + ", "

    py_file = imports + get_sys + ']\n\n\n'

    get_F = ("def get_F(sol):\n"
             "\tF = " + fluo_eq + "\n"
             "\treturn F\n")

    py_file = py_file + get_F

    if is_valid_code(py_file):
        # Safely write/replace get_system.py without pre-deleting
        try:
            _write_atomic("get_system.py", py_file)
        except PermissionError as e:
            # Last resort: attempt to chmod then retry
            try:
                if os.path.exists("get_system.py"):
                    os.chmod("get_system.py", 0o664)
                _write_atomic("get_system.py", py_file)
            except Exception as e2:
                print(f"Failed to write get_system.py due to permissions: {e2}")
                return False
        except Exception as e:
            print(f"Failed to write get_system.py: {e}")
            return False

        # Wait until file is visible (rare, but keeps previous logic)
        for _ in range(10):
            if os.path.exists('get_system.py'):
                break
            time.sleep(0.1)

        print("New get_system.py written.")
        return True

    else:
        return False


def is_valid_code(code_text):
    try:
        ast.parse(code_text)
        return True
    except SyntaxError as e:
        print(f"Invalid code : error in syntax")
        return False


def elem_to_latex(elem):
    latex_result = sp.latex(sp.sympify(elem, evaluate=True), mul_symbol="\\cdot ")
    latex_result = latex_result.replace('neg', r'{\text{-1}}')
    latex_result = latex_result.replace('zero', r'{\text{0}}')
    return latex_result


def clear_queue(q):
    while not q.empty():
        q.get()


def convert_to_latex(equation):
    system, system_eq = equation.split("=")
    latex_result = elem_to_latex(system) + " = " + elem_to_latex(system_eq)
    return latex_result


def system_to_latex(eq_system):
    eq_system = eq_system.replace('$', '')
    eq_system = eq_system.replace('neg', '^neg')
    eq_system = eq_system.replace('zero', '^zero')
    system = eq_system.split('\n')
    latex = []

    for eq in system:
        latex.append(convert_to_latex(eq))

    return latex


def get_X_list(system_text):
    X_list = re.findall(r'\bX\d+\b', system_text)
    return list(dict.fromkeys(X_list))


def load_dataset():
    params_file = "dataset/metrics_npq_score.csv"
    metrics_file = "dataset/params_npq_score.csv"

    if os.path.exists(params_file) and os.path.exists(metrics_file):
        data_params = pd.read_csv(params_file)
        data_metrics = pd.read_csv(metrics_file)

        return data_params, data_metrics

    else:
        print("Missing dataset.")
        return pd.DataFrame, pd.DataFrame


def normalize_data(data, norm_param):
    data = np.array(data)
    if norm_param['val'] == 'mean':
        val = np.mean(data)
    else:
        val = data[int(norm_param['val'])]

    if norm_param['type'] == 'div':
        data = data/val
    else:
        data = data-val
    return data


def get_color_gradient(n, cmap_name="viridis"):
    cmap = plt.get_cmap(cmap_name)  # Choix du colormap
    return [f"rgb({int(cmap(i/n)[0]*255)}, {int(cmap(i/n)[1]*255)}, {int(cmap(i/n)[2]*255)})" for i in range(n)]


def get_pars_name():
    with open("memory.json", "r") as m:
        memory = json.load(m)

    pars_dict = memory['variable_params']

    sorted_pars = dict(sorted(pars_dict.items()))
    names = []

    for p in sorted_pars:
        names.append(p)

    return names


def associate_pars(values):
    pars = {}
    pars_names = get_pars_name()
    for i, val in enumerate(values):
        pars[pars_names[i]] = val
    return pars


def get_csv_name(col):
    file_dict = {}
    col = col.rsplit(' - ', 1)
    file_dict['type'] = 'csv'
    file_dict['name'] = col[0]
    if len(col) == 2:
        file_dict['col'] = col[1]
    return file_dict


def get_series_name(name):
    name = name.split(' - ')
    if name[0] == 'csv':
        series = {
            'type': 'csv',
            'name': name[1],
            'col': name[2]
        }
    else:
        series = {
            'type': 'dataframe',
            'name': name[1],
            'col': name[2]
        }

    return series


def fit_result_to_dict(result, verbose: bool = False):
    res_dict = {
        'xopt': associate_pars(result[0]),
        'fopt': result[1].item(),
        'iterations': result[2],
        'evals': result[3]
    }

    if verbose:
        try:
            print("[fit_result_to_dict] Optimization summary:", flush=True)
            # Parameter breakdown
            xopt_items = ", ".join([f"{k}={v:.6g}" for k, v in res_dict['xopt'].items()])
            print(f"  xopt: {xopt_items}", flush=True)
            print(f"  fopt: {res_dict['fopt']}", flush=True)
            print(f"  iterations: {res_dict['iterations']}", flush=True)
            print(f"  evals: {res_dict['evals']}", flush=True)
        except Exception as e:
            print(f"[fit_result_to_dict] Verbose printing failed: {e}", flush=True)

    return res_dict


def run_result_to_dict(result, err):
    print(result)
    res_dict = {
        'x0': associate_pars(result),
        'fopt': err,
    }

    return res_dict


def get_sys_dimension():
    with open("memory.json", "r") as m:
        memory = json.load(m)
    system = memory['raw_system'].split('\n')
    if '' in system:
        system.remove('')
    return len(system)


def save_latex_as_image(destination=None, fontsize=20, dpi=300):
    # Allow disabling via env or when pdflatex is unavailable
    if os.getenv("DISABLE_LATEX_IMAGE", "0").lower() in ("1", "true", "yes"):
        return None
    if shutil.which("pdflatex") is None:
        print("pdflatex not found; skipping LaTeX image generation.")
        return None
    with open("memory.json", "r") as m:
        memory = json.load(m)

    equations = memory['latex']
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "equations.tex")
        latex_body = r" \\".join(r"&" + eq for eq in equations)

        tex_content = r"""
        \documentclass[preview]{standalone}
        \usepackage{amsmath}
        \usepackage{amssymb}
        \begin{document}
        \setlength{\jot}{3mm}
        \begin{flalign*}
        """ + latex_body + r""" &&
        \end
        {flalign*}
        \end
        {document}
        """

        # Écrire le .tex
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)

        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "equations.tex"],
                cwd=os.path.abspath(tmpdir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
        except FileNotFoundError:
            print("pdflatex not available; skipping LaTeX image generation.")
            return None
        except subprocess.CalledProcessError as e:
            print("Erreur pdflatex:")
            print(e.stdout.decode())
            print(e.stderr.decode())
            return None

        pdf_path = os.path.join(tmpdir, "equations.pdf")
        images = convert_from_path(pdf_path, dpi=300)

        # Sauvegarder la première page dans un buffer mémoire
        img_buffer = io.BytesIO()
        images[0].save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return img_buffer


def save_bytesio_to_tempfile(buffer, suffix=".png"):
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmpfile.write(buffer.getvalue())
    tmpfile.close()
    return tmpfile.name
