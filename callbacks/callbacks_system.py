from app import app
import dash
from dash import Input, Output, State, dcc, html
import os
import dash_bootstrap_components as dbc
import pandas as pd
import json
import tools as pt


# Callback pour exécuter la fonction et mettre à jour les Fixed Params
@app.callback(
    [Output("fixed-params-container", "children"),
     Output("variable-params-container", "children"),
     Output("x-container", "children"),
     Output("latex-container", "children"),
     Output("valid-icon", "style"),
     Output('valid-icon', 'className')],
    [Input("get-params", "n_clicks"),
     Input("save-params", "n_clicks")],
    [State("system-input", "value"),
     State("fluo-input", "value"),
     State("fixed-params-container", "children"),
     State("variable-params-container", "children"),
     State("x-container", "children"),
     State("pfd-container", "children"),
     State('valid-icon', 'className')
     ],
    prevent_initial_call=False
)
def update_params(get_clicks, save_clicks, system_text, fluo_text, fixed_children, variable_children, x_children, pfd_children, valid_icon):
    ctx = dash.callback_context
    msg_color = {}
    x_list = pt.get_X_list(system_text)

    # Vérification des conteneurs
    if fixed_children is None:
        fixed_children = []

    if variable_children is None:
        variable_children = []

    if not x_children:
        x_params = {
            x: x
            for x in x_list
        }

    else:
        if len(x_children) > len(x_list):
            x_children = x_children[:len(x_list)]

        x_params = {
            x_list[i]: child['props']['children'][1]['props']['value']
            for i, child in enumerate(x_children)
            if child and isinstance(child, dict) and 'props' in child and 'children' in child['props']
        }

    # Stocker les paramètres sous forme de dictionnaires
    fixed_params = {
        child['props']['children'][0]['props']['value']: child['props']['children'][1]['props']['value']
        for child in fixed_children
        if child and isinstance(child, dict) and 'props' in child and 'children' in child['props']
    }

    variable_params = {
        child['props']['children'][0]['props']['value']: child['props']['children'][1]['props']['value']
        for child in variable_children
        if child and isinstance(child, dict) and 'props' in child and 'children' in child['props']
    }

    pfd_params = {
        child['props']['children'][0]['props']['value']: child['props']['children'][1]['props']['value']
        for child in pfd_children
        if child and isinstance(child, dict) and 'props' in child and 'children' in child['props']
    }

    # If "Get Params" is clicked
    if ctx.triggered_id == "get-params":
        results = pt.get_params(system_text if system_text else "")

        if os.path.exists("memory.json"):
            with open("memory.json", "r") as m:
                memory = json.load(m)
                fixed_pars = memory.get('fixed_params', {})
                variable_pars = memory.get('variable_params', {})
                x_pars = memory.get('x_names', {})

            fixed_params = {}
            variable_params = {}
            x_params = {}

            for result in results[0]:
                if result in fixed_pars:
                    fixed_params[result] = fixed_pars[result]
                else:
                    fixed_params[result] = ""

            for result in results[1]:
                if result in variable_pars:
                    variable_params[result] = variable_pars[result]
                else:
                    variable_params[result] = ""

            for x in x_list:
                if x in x_pars:
                    x_params[x] = x_pars[x]
                else:
                    x_params[x] = x

        valid_model = pt.generate_py_file(system_text, fluo_text)

        if not valid_model:
            msg_color = {"color": "red", "fontSize": "40px"}
            valid_icon = "fa-solid fa-circle-xmark"

        else:
            msg_color = {"color": "green", "fontSize": "40px"}
            valid_icon = "fa-solid fa-circle-check"

    # Reconstruire les conteneurs à partir des dictionnaires
    fixed_children = [
        html.Div([
            dbc.Input(value=var, type="text", disabled=True, style={'width': '45%', 'marginLeft': '10px'}),
            dbc.Input(value=value, placeholder="Enter value", id={'type': 'fixed-param-value', 'index': i}, style={'width': '45%', 'marginLeft': '10px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center'})
        for i, (var, value) in enumerate(fixed_params.items())
    ]

    variable_children = [
        html.Div([
            dbc.Input(value=var, type="text", disabled=True, style={'width': '45%', 'marginLeft': '10px'}),
            dbc.Input(value=value, placeholder="Enter value", id={'type': 'variable-param-value', 'index': i}, style={'width': '45%', 'marginLeft': '10px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center'})
        for i, (var, value) in enumerate(variable_params.items())
    ]

    x_children = [
        html.Div([
            dcc.Markdown(f'$${pt.elem_to_latex(var) + " ="}$$', mathjax=True, style={'marginTop': '10px', 'marginLeft': '10px'}),
            dbc.Input(value=value, placeholder="Enter value", id={'type': 'x-value', 'index': i},
                      style={'width': '80px', 'marginLeft': '10px'}),
        ], style={'marginBottom': '0px', 'display': 'flex', 'alignItems': 'center'})
        for i, (var, value) in enumerate(x_params.items())
    ]

    for var in variable_params:
        variable_params[var] = pt.convert_to_float(variable_params[var])

    for var in fixed_params:
        fixed_params[var] = pt.convert_to_float(fixed_params[var])

    for var in pfd_params:
        pfd_params[var] = pt.convert_to_float(pfd_params[var])

    if system_text != '':
        x_system_text = system_text
        for x in x_params:
            x_system_text = x_system_text.replace(x, x_params[x])

        latex_system = pt.system_to_latex(x_system_text)

        latex = [
            html.Div([
                dcc.Markdown(
                    f'$${eq}$$',
                    mathjax=True
                ),
            ])
            for eq in latex_system
        ]

    else:
        latex_system = ''
        latex = ''

        # Mise à jour de memory.json
    memory_data = {
        'raw_system': system_text,
        'fluo_equation': fluo_text,
        'variable_params': variable_params,
        'fixed_params': fixed_params,
        'pfd_params': pfd_params,
        'latex': latex_system,
        'x_names': x_params
    }

    if system_text != '':
        with open("memory.json", "w") as mem:
            json.dump(memory_data, mem)

    return fixed_children, variable_children, x_children, latex, msg_color, valid_icon