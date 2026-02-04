import io
import json
import os.path
import pandas as pd
from app import app
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


@app.callback(
    Output('filter-container', 'children'),
    Input('column-selector', 'value')
)
def update_filter_options(selected_columns):

    df = pd.read_csv("dataset/params_npq_score.csv")

    if not selected_columns:
        return []

    filters = []
    for col in selected_columns:
        unique_values = df[col].dropna().unique()
        filters.append(
            html.Div([
                html.Label(f"Filtrer par {col}"),
                dcc.Dropdown(
                    id={'type': 'filter-dropdown', 'index': col},
                    options=[{'label': str(val), 'value': val} for val in unique_values],
                    placeholder=f"Sélectionner une valeur pour {col}",
                    multi=True
                )
            ])
        )
    return filters


@app.callback(
    Output('filtered-table', 'data'),
    Input('column-selector', 'value'),
    Input({'type': 'filter-dropdown', 'index': dash.ALL}, 'value')
)
def filter_data(selected_columns, filter_values):
    df = pd.read_csv("dataset/params_npq_score.csv")

    if not selected_columns or not filter_values:
        return df.to_dict('records')

    filtered_df = df.copy()
    for col, values in zip(selected_columns, filter_values):
        if values:
            filtered_df = filtered_df[filtered_df[col].isin(values)]

    return filtered_df.to_dict('records')


@app.callback(
    Output("table-collapse", "is_open"),
    Output("chevron-icon", "className"),
    Input("toggle-button", "n_clicks"),
    State("table-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_table(n_clicks, is_open):
    """Bascule entre ouvert et fermé et change l'icône de la flèche."""
    is_open = not is_open  # Alterne l'état du collapse
    icon = "fa-solid fa-chevron-up" if is_open else "fa-solid fa-chevron-down"  # Change l'icône
    return is_open, icon