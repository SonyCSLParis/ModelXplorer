# app.py
from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"
    ],
    suppress_callback_exceptions=True
)

server = app.server