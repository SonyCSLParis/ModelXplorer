from dash import html
import dash_bootstrap_components as dbc


def get_menu():
    return html.Div([
        dbc.Button([
            html.I(id="save-icon", className="fa-solid fa-floppy-disk",
                   style={"fontSize": "50px", "color": "white"}),
            "Save params"],
            id='save-params', color=None, className='mt-3 main-button',
            style={"backgroundColor": "#0d6efd", "color": "white"}),

        dbc.Button([
            html.I(id="get-data-icon", className="fa-solid fa-chart-line",
                   style={"fontSize": "50px", "color": "white"}),
            "Get data"
        ], id="get-data", color=None, className='mt-3 main-button',
            style={"backgroundColor": "#6610f2", "color": "white"}),

        dbc.Button(
            [html.I(id="run-icon", className="fa-solid fa-play", style={"fontSize": "50px", "color": "white"}),
             "Run Model"],
            id='run-model', color=None, className='mt-3 main-button',
            style={"backgroundColor": "#d63384", "color": "white"}),

        dbc.Button([html.I(id="fit-icon", className="fa-solid fa-forward",
                           style={"fontSize": "50px", "color": "white"}),
                    "Fit Model"],
                   id='fit-function', color=None, className='mt-3 main-button',
                   style={"backgroundColor": "#fd7e14", "color": "white"}),

        dbc.Button([
            html.I(id="screenshot-icon", className="fa-solid fa-camera",
                   style={"fontSize": "50px", "color": "white"}),
            "Download screenshot",
        ], id="download-btn", color=None, className='mt-3 main-button',
            style={"backgroundColor": "#ffc107", "color": "white"}),

        dbc.Button([
            html.I(id="download-icon", className="fa-solid fa-file-export",
                   style={"fontSize": "50px", "color": "white"}),
            "Go to omniboard",
        ], id="export-btn", color=None, className='mt-3 main-button', href="http://localhost:9000/sacred",
            style={"backgroundColor": "#198754", "color": "white"}),

    ], style={'position': 'fixed', 'justifyContent': 'right', 'bottom': '20px', 'right': '100px',
              'zIndex': '1000', 'display': 'flex', 'gap': '20px', 'fontSize': '5px'})
