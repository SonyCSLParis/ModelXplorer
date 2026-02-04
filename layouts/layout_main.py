# layouts/layout_main.py
import os
import json
import pandas as pd
from dash import html, dcc, Input, Output, State, dash_table
from layouts.layout_left_panel import get_left_panel
from layouts.layout_right_panel_onefit import get_panel_onefit
from layouts.layout_right_panel_batch import get_panel_batch
from config.config import VERSION


def create_layout():
    pfd = {
        "flash": "",
        "light": "",
        "dark": "",
        "PFDTs": "",
    }

    if os.path.exists("memory.json"):
        with open("memory.json", "r") as m:
            memory = json.load(m)
            eq_system = memory.get('raw_system', "")
            fixed_pars = memory.get('fixed_params', {})
            variable_pars = memory.get('variable_params', {})
            pfd_pars = memory.get('pfd_params', pfd)
            fluo_eq = memory.get('fluo_equation', "")
            latex = memory.get('latex', [])
            x_pars = memory.get('x_names', {})
    else:
        eq_system = ""
        fixed_pars = {}
        variable_pars = {}
        pfd_pars = pfd
        fluo_eq = ""
        latex = []
        x_pars = {}

    if VERSION == "onefit":
        df = pd.read_csv('dataset/params_npq_score.csv')
        right_panel = get_panel_onefit(df)

    else:
        right_panel = get_panel_batch()

    layout = html.Div(id='layout', style={'display': 'flex', 'gap': '10px', 'marginBottom': '50px', "border-right": "1px solid #ccc"}, children=[
        dcc.Interval(id="page-load", interval=1, max_intervals=1),
        get_left_panel(eq_system, x_pars, fixed_pars, variable_pars, pfd_pars, fluo_eq, latex),

        html.Div(style={
            'width': '1px',
            "backgroundColor": "#ccc",
            "margin": "1%"
        }),

        right_panel,

    ])

    return layout


def get_layout():
    return create_layout()
