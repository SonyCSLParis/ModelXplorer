import io
import json
import os, os.path
import pandas as pd
import dash
import numpy as np
import dash_daq as daq
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import tools as pt
import plotly.graph_objs as go
import base64
import model_new as mod
import multiprocessing
import fit_params_parallel as fit
from tosacred.SendExperiment import send_experiment
from app import app

F_queue = None
n = 10
max_series = 1000


def _plot_verbose() -> bool:
    # Use VERBOSE or PLOT_VERBOSE to enable plotting logs
    v = os.getenv("PLOT_VERBOSE")
    if v is None:
        v = os.getenv("VERBOSE", "0")
    return str(v).lower() in ("1", "true", "yes", "on", "debug")


def _plog(msg: str):
    if _plot_verbose():
        print(f"[Plot] {msg}", flush=True)


def set_F_queue(queue):
    global F_queue
    F_queue = queue


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
    Output("norm-value", "style"),
    Input("norm-mean", "value")
)
def toggle_input(selected_value):
    if selected_value == "index":
        return {"display": "inline-block", "marginLeft": "0px", "width": "50px"}
    return {"display": "none"}


@app.callback(
    Output("data-dataset", "data"),
    Output("data-params", "data"),
    Output("norm-value", "max"),
    Input("page-load", "n_intervals"),
    Input("get-data", "n_clicks"),
    Input('filtered-table', 'data')
)
def get_data(n_intervals, n_clicks, stored_data):
    pt.clear_queue(F_queue)
    data_params = pd.DataFrame(stored_data)
    data_params = data_params.sample(n=1)
    data = pt.get_data(data_params)

    return data, data_params.to_dict('records'), len(data)-1


# Callback pour get and store F (queue)
@app.callback(
    Output('data-store', 'data'),
    Input('interval-update', 'n_intervals'),
    State('data-store', 'data')
)
def update_store(n_intervals, store_data):
    # Ensure store schema
    if not isinstance(store_data, dict):
        store_data = {}
    store_data.setdefault('F_values', [])
    store_data.setdefault('done', False)
    store_data.setdefault('last_summary', None)

    F_counter = 0

    while F_queue is not None and not F_queue.empty() and F_counter < n:
        item = F_queue.get()
        # Completion sentinel from fitter
        if isinstance(item, dict) and item.get('_done'):
            summary = {k: v for k, v in item.items() if k != '_done'}
            store_data['done'] = True
            store_data['last_summary'] = summary if summary else None
            _plog(f"Received completion sentinel | summary={summary}")
        # Normal F-series (list/array of values)
        elif isinstance(item, (list, tuple)):
            # New incoming data implies an active run; clear any prior 'done'
            if store_data.get('done'):
                store_data['done'] = False
                store_data['last_summary'] = None
            store_data['F_values'].append(list(item))
            F_counter += 1

            # Limit the number of stored series
            if len(store_data['F_values']) > max_series:
                store_data['F_values'].pop(0)
        else:
            # Unknown item type; ignore gracefully
            _plog(f"Ignored queue item of type {type(item)}")

    return store_data


@app.callback(
    Output('live-graph', 'style'),
    Output('interval', 'disabled'),
    Input('download-btn', 'n_clicks'),
    Input('interval', 'n_intervals'),
    State('live-graph', 'style')
)
def update_image_size(n_clicks, n_intervals, current_style):
    ctx = dash.callback_context

    if not ctx.triggered:
        return current_style, True

    if ctx.triggered_id == 'download-btn':
        return {'width': '1050px'}, False
    elif ctx.triggered_id == 'interval':
        # Restaure the size and deactivate the interval
        return {'width': '100%'}, True

    return current_style, True


@app.callback(
    Output('data-to-fit', 'data'),
    Output('data-fit-selector', 'options'),
    Output('selected-data-name', 'data'),
    Input('data-fit-selector', 'value'),
    Input('data-dataset', 'data'),
    Input('csv-series', 'data'),
    Input('data-params', 'data')
)
def choose_data_to_fit(selector, data, data_csv, data_params):
    options = ['data']

    for series in data_csv:
        options.append(series)

    if selector != 'data':
        data_csv = data_csv[selector]
        data = []
        selected_data = f"csv - {selector}"
        for d in data_csv:
            data.append(float(d))
    else:
        selected_data = f"dataframe - {data_params[0]['run_id']} - {data_params[0]['algae']}"# - {data_params} - {}"

    return data, options, selected_data


@app.callback(
    Output('interval-update', 'disabled'),
    [Input('fit-function', 'n_clicks'),
     Input('run-model', 'n_clicks'),
     Input('data-to-fit', 'data'),
     Input('normalization', 'data'),
     Input('selected-data-name', 'data')],
    prevent_initial_call=True
)
def run_model(fit_clicks, run_clicks, data, norm, selected_data):
    ctx = dash.callback_context

    if ctx.triggered_id and data:
        data = pt.normalize_data(data, norm)
        pars0 = mod.get_pars0()
        pars = mod.get_pars()

        # If "Fit function" is clicked
        if ctx.triggered_id == "fit-function":
            pt.clear_queue(F_queue)
            process = multiprocessing.Process(target=run_fit, args=(data, pars, pars0, 0, 0, F_queue, norm, selected_data))
            process.start()
            return False

        # If "Run model" is clicked
        if ctx.triggered_id == "run-model":
            pt.clear_queue(F_queue)
            process = multiprocessing.Process(target=run_get_error, args=(pars, data, pars0, F_queue, norm, selected_data))
            process.start()
            return False

    return True


@app.callback(
    Output('live-graph', 'figure'),
    Input('data-store', 'data'),
    Input('data-to-fit', 'data'),
    Input('toggle-switch', 'value'),
    Input('radio-selection', 'value'),
    Input('number-curves', 'value'),
    Input('series-checklist', 'value'),
    Input('normalization', 'data'),
    State('csv-series', 'data'),
)
def update_graph(store_data, data, show_data, radio, n_fit, csv_checklist, norm, csv_data):
    fig = go.Figure()

    data = pt.normalize_data(data, norm)

    if not show_data:
        _plog(f"Plotting base data | len={len(data)} | norm={norm}")
        fig.add_trace(go.Scatter(
                y=data,
                mode='lines',
                name=f'data',
                line=dict(color='crimson', width=2)
            ))

    total_series = len(store_data['F_values'])

    colors_csv = pt.get_color_gradient(len(csv_checklist), cmap_name="tab20b")

    for i, name in enumerate(csv_checklist):
        trace = pt.normalize_data(csv_data[name], norm)
        _plog(f"Overlay CSV series '{name}' | len={len(trace)}")
        fig.add_trace(go.Scatter(
            y=trace,
            mode='lines',
            name=name,
            line=dict(color=colors_csv[i], width=2)
        ))

    if radio == "every":
        selected_series = [(i, store_data['F_values'][i]) for i in range(len(store_data['F_values'])) if i % n_fit == 0]
    elif radio == "first":
        selected_series = [(i, store_data['F_values'][i]) for i in range(min(n_fit, total_series))]
    elif radio == "last":
        total_series = len(store_data['F_values'])
        selected_series = [(i, store_data['F_values'][i]) for i in range(max(0, total_series-n_fit), total_series)]
    else:
        selected_series = []  # Default case if nothing is selected

    n_curves = len(selected_series)
    _plog(f"Plotting {n_curves} fit curve(s) | mode={radio} | step={n_fit} | total_store={total_series}")
    if n_curves:
        _plog(f"Fit indices: {[i for i, _ in selected_series]}")
    colors = pt.get_color_gradient(n_curves, cmap_name="PuBu")

    for i, (index, F_series) in enumerate(selected_series):
        if i == len(selected_series) - 1:
            color = 'darkviolet'
        else:
            color = colors[i]
        try:
            _plog(f"Adding fit trace idx={index} | len={len(F_series)} | min={np.min(F_series):.4g} | max={np.max(F_series):.4g}")
        except Exception:
            _plog(f"Adding fit trace idx={index} | len={len(F_series)}")
        fig.add_trace(go.Scatter(
            y=F_series,
            mode='lines',
            name=f'fit {index + 1}',
            line=dict(color=color, width=2)
        ))

    # Compose optional title if fit has completed
    title_text = None
    try:
        done = bool(store_data.get('done')) if isinstance(store_data, dict) else False
    except Exception:
        done = False
    if done:
        summary = store_data.get('last_summary') or {}
        parts = ["Fit complete"]
        if isinstance(summary, dict):
            if 'evals' in summary:
                parts.append(f"evals={summary['evals']}")
            if 'iters' in summary:
                parts.append(f"iters={summary['iters']}")
            if 'fopt' in summary:
                try:
                    parts.append(f"MSE={float(summary['fopt']):.4g}")
                except Exception:
                    parts.append(f"MSE={summary['fopt']}")
        title_text = " | ".join(parts)
        _plog(f"Annotating figure title: {title_text}")

    fig.update_layout(
        autosize=True,
        xaxis_title="Index",
        yaxis_title="Fluorescence",
        title=title_text,
        plot_bgcolor='white',
        margin=dict(l=0, r=0, t=(40 if title_text else 0), b=0),
    )

    fig.update_xaxes(showgrid=True, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridcolor='LightGrey')

    return fig


@app.callback(
    Output('csv-series', 'data'),
    Output('series-checklist', 'options'),
    Output('series-checklist', 'value'),
    Output('data-fit-selector', 'value'),
    Input('upload-data', 'contents'),
    State('csv-series', 'data'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_series(contents, stored_data, filenames):
    if contents is None:
        # Must return 4 outputs: data, options, value, default selector
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    if not isinstance(stored_data, dict):
        stored_data = {}

    added_series = []

    for content, filename in zip(contents, filenames):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Verify that there are columns
        if df.shape[1] < 1:
            continue  # Ignore the file

        # Add each column from the CSV as a distinct series
        for col in df.columns:
            series_name = f"{filename} - {col}"
            stored_data[series_name] = df[col].tolist()  # Store the column's values
            added_series.append(series_name)

    # Mettre à jour les options de la checklist
    options = [{'label': '  ' + name, 'value': name} for name in stored_data.keys()]

    # Default the fit selector to the first newly added series (if any),
    # so clicking "Fit" immediately uses the uploaded data.
    default_selector = added_series[0] if added_series else dash.no_update

    # Select all series in checklist by default (including newly added)
    return stored_data, options, list(stored_data.keys()), default_selector


def run_fit(data, pars, pars0, i, N, queue, norm, series_name):
    print(f"[Fit] Starting single-trace fit | series={series_name} | len={len(data)} | norm={norm}", flush=True)
    # For single-trace runs, pass total=1 for cleaner logs
    res_pars = fit.get_pars(data, pars, pars0, 0, 1, queue, norm)
    print("[Fit] Finished fit; sending to Sacred...", flush=True)
    send_experiment(pt.get_csv_name(series_name), data, res_pars, norm, 'fit')


def run_get_error(pars, data, pars0, queue, norm, series_name):
    print(f"[Fit] Running model (no optimization) | series={series_name} | len={len(data)} | norm={norm}", flush=True)
    res_pars = fit.get_Ferr(pars, data, pars0, norm, queue)
    print("[Fit] Model run done; sending to Sacred...", flush=True)
    send_experiment(pt.get_csv_name(series_name), data, res_pars, norm, 'run')
