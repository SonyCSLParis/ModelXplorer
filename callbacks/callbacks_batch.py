# callbacks/model_callbacks_multifit.py
import numpy as np
import os
from dash import Input, Output, State, html, dcc
from dash import callback_context as ctx
import dash
import pandas as pd
import io
import base64
import model_new as mod
import fit_params_parallel as fit
import tools as pt
from app import app
import multiprocessing
from tosacred.SendExperiment import send_experiment
import time
from multiprocessing import Process, Queue

F_queue = None
running_series = []
fit_results = {}


def set_F_queue(queue):
    global F_queue
    F_queue = queue


def fit_wrapper(series_name, data, norm, queue):
    data = pt.normalize_data(data, norm)
    pars0 = mod.get_pars0()
    pars = mod.get_pars()
    res_pars = fit.get_pars(data, pars, pars0, 0, 0, queue=None, norm=norm)
    send_experiment(pt.get_csv_name(series_name), data, res_pars, norm)
    result = {
        'series': series_name,
        'status': '✅ done',
        'fit_result': res_pars[0],
    }
    queue.put(result)


@app.callback(
    Output("normalization", "data"),
    Input("norm-type", "value"),
    Input("norm-mean", "value"),
    Input("norm-value", "value"),
)
def get_normalization(norm_type, mean, value):
    norm = {'val': mean if mean == "mean" else 0 if mean is None else str(value), 'type': norm_type}
    return norm


@app.callback(
    Output('multifit-preview-table', 'data'),
    Output('multifit-preview-table', 'columns'),
    Output('multifit-series-data', 'data'),
    Input('upload-multifit-data', 'contents'),
    State('upload-multifit-data', 'filename'),
    State('no-header-option', 'value'),
    prevent_initial_call=True
)
def handle_multiple_csvs(list_of_contents, list_of_names, no_header_option):
    if list_of_contents is None:
        return dash.no_update, dash.no_update, dash.no_update

    series_data = {}
    preview_df = pd.DataFrame()

    has_header = 'no_header' not in no_header_option

    for content, name in zip(list_of_contents, list_of_names):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=0 if has_header else None)

        # Génère des noms de colonnes si pas d’en-tête
        if not has_header:
            if df.shape[1] == 1:
                df.columns = [name]  # nom du fichier s’il n’y a qu’une seule colonne
            else:
                df.columns = [f"{name} - col{i}" for i in range(len(df.columns))]
        else:
            df.columns = [f"{name} - {df.columns[i]}" for i in range(len(df.columns))]

        for col in df.columns:
            series_data[col] = df[col].dropna().tolist()
            preview_df[col] = series_data[col]

    columns = [{"name": col, "id": col} for col in preview_df.columns]

    return preview_df.to_dict('records'), columns, series_data


@app.callback(
    Output('multifit-series-cards', 'children'),
    Input('multifit-status-data', 'data'),
    Input('multifit-results', 'data'),
    prevent_initial_call=True
)
def display_series_status_cards(status_dict, fit_results):
    pars = pt.get_pars_name()

    if not status_dict:
        return []

    cards = []
    for name, status in status_dict.items():
        result = ""
        if fit_results and name in fit_results and fit_results[name] is not None:
            values = fit_results[name][0]
            result = html.Div([
                html.Small(f"Result: "),
                html.Ul([html.Li(f"{pars[i]}: {v:.6f}") for i, v in enumerate(values)])
            ])

        card = html.Div([
            html.H6(name, style={'fontWeight': 'bold'}),
            html.Div(status),
            html.Div(result)
        ], style={
            'border': '1px solid #ccc',
            'borderRadius': '10px',
            'padding': '10px',
            'width': '240px',
            'boxShadow': '2px 2px 5px rgba(0,0,0,0.1)',
            'backgroundColor': '#f9f9f9'
        })
        cards.append(card)

    return cards


@app.callback(
    Output('multifit-status-data', 'data'),
    Output('multifit-results', 'data'),
    Output('interval-refresh-status', 'disabled'),
    Input('start-multifit', 'n_clicks'),
    Input('interval-refresh-status', 'n_intervals'),
    Input('multifit-series-data', 'data'),
    Input("normalization", "data"),
    State('multifit-series-data', 'data'),
    State('multifit-status-data', 'data'),
    prevent_initial_call=True
)
def _get_int_env(name, default):
    try:
        v = os.getenv(name)
        return int(v) if v is not None and str(v).strip() != "" else default
    except Exception:
        return default


def handle_multifit(start_clicks, interval_tick, uploaded_series, norm, series_data, status_data):
    global running_series, fit_results, F_queue

    if uploaded_series and not series_data:
        series_data = uploaded_series

    if not series_data:
        return dash.no_update, dash.no_update, dash.no_update

    if not status_data or len(status_data) != len(series_data):
        status_data = {name: "🟡 waiting" for name in series_data}
        return status_data, dash.no_update, True

    # Determine safe parallelism
    max_procs_env = _get_int_env("BATCH_MAX_PROCS", None)
    cpu_procs = max(1, multiprocessing.cpu_count() - 1)
    n_cores = max_procs_env if (isinstance(max_procs_env, int) and max_procs_env > 0) else cpu_procs
    triggered_id = ctx.triggered_id

    if triggered_id == "start-multifit":
        print(f'Number of cores available : {n_cores}')

        # Réinitialisation complète
        running_series = list(series_data.keys())
        fit_results = {}

        for i in range(min(n_cores, len(running_series))):
            name = running_series.pop(0)
            status_data[name] = "🟠 running"
            p = Process(target=fit_wrapper, args=(name, series_data[name], norm, F_queue))
            p.start()

        return status_data, dash.no_update, False

    elif triggered_id == "interval-refresh-status":
        active_fits = sum(1 for status in status_data.values() if status == "🟠 running")

        while not F_queue.empty():
            result = F_queue.get()
            status_data[result['series']] = result['status']
            fit_results[result['series']] = result['fit_result']
            active_fits -= 1

        while running_series and active_fits < n_cores:
            name = running_series.pop(0)
            status_data[name] = "🟠 running"
            p = Process(target=fit_wrapper, args=(name, series_data[name], norm, F_queue))
            p.start()
            active_fits += 1

        all_done = all(status != "🟠 running" for status in status_data.values())
        return status_data, fit_results, all_done

    return dash.no_update, dash.no_update, dash.no_update