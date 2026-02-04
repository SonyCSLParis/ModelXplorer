from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from layouts.layout_menu import get_menu
from layouts.layout_norm import get_norm
import dash_daq as daq


def get_panel_batch():
    return html.Div(style={
            'width': '50%',
        }, children=[

        html.H4("Multi-Series Fit Panel", style={'textAlign': 'center', 'marginTop': '10px'}),

        html.Div([
            html.Label("Import CSV file with multiple series:"),
            dcc.Checklist(
                id='no-header-option',
                options=[{'label': "File(s) without header", 'value': 'no_header'}],
                value=[],
                style={'padding': '10px'}
            ),
            dcc.Upload(
                id='upload-multifit-data',
                children=html.Div([
                    html.Div(style={'display': 'inline-block'}, children=[
                        html.Div(["Drop CSV here"], style={
                            # 'width': '100%',
                            'height': '60px',
                            'fontSize': '15px',
                            'lineHeight': '80px',
                            'borderWidth': '2px',
                            'borderStyle': 'dashed',
                            'borderRadius': '10px',
                            'textAlign': 'center',
                            'padding': '30px',
                            'backgroundColor': '#f9f9f9',
                            'cursor': 'pointer',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                        }),
                    ]),

                    html.Label("or", style={'display': 'inline-block', 'padding': '20px'}),

                    # ✅ Bouton Upload
                    html.Button("Upload CSV", className='btn btn-primary', style={
                        'width': '150px', 'height': '60px', 'color': '#ffffff',
                        'backgroundColor': '#007bff', 'border': 'none',
                        'fontWeight': 'bold', 'borderRadius': '10px',
                        'cursor': 'pointer', 'fontSize': '15px',
                        'display': 'inline-block',
                        'alignItems': 'center',
                        'justifyContent': 'center'
                    })
                ]),
                multiple=True,
                style={'display': 'flex', 'width': '400px', 'justifyContent': 'left', 'alignItems': 'center'}
            )
        ], style={'marginBottom': '20px'}),

        html.H5("Preview of uploaded data:", style={'marginTop': '20px'}),
        dash_table.DataTable(
            id='multifit-preview-table',
            page_size=5,
            style_table={'overflowX': 'auto'}
        ),

        get_norm(),
        dcc.Store(id='multifit-series-data'),
        dcc.Store(id='multifit-status-data'),
        dcc.Store(id='multifit-results'),

        html.H5("Fitting status per series:", style={'marginTop': '30px'}),
        html.Div(id='multifit-series-cards', style={
            'display': 'flex', 'flexWrap': 'wrap', 'gap': '15px'
        }),

        dcc.Store(id='normalization'),

        dbc.Button("Start Multi-Fit", id="start-multifit", className="btn btn-success", style={'marginTop': '30px'}),
        dcc.Interval(id='interval-refresh-status', interval=1000, disabled=True),

        get_menu()
    ])
