from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import dash_daq as daq
from layouts.layout_menu import get_menu
from layouts.layout_norm import get_norm


def get_panel_onefit(df):
    return html.Div(style={
            'width': '50%',
        }, children=[
            html.Button(
                html.Div([
                    html.H4("Dataset filtering", style={'textAlign': 'center', 'padding': '10px'}),
                    html.I(id="chevron-icon", className="fa-solid fa-chevron-down"),
                ], style={"display": "flex", "alignItems": "center", "width": "100%", "justifyContent": "center"}),
                # Aligner le texte et l'icône
                id="toggle-button",
                n_clicks=0,
                style={
                    "backgroundColor": "white", "border": "none", "cursor": "pointer", "width": "100%",
                    "display": "flex", "alignItems": "center", "fontSize": "16px", "textAlign": "center",
                    "justifyContent": "center"
                }
            ),

            dbc.Collapse(
                html.Div([
                    # Dropdown menu to select a column
                    dcc.Dropdown(
                        id='column-selector',
                        options=[{'label': col, 'value': col} for col in df.columns],
                        placeholder="Select a column",
                        multi=True
                    ),

                    # Conteneur pour les filtres dynamiques
                    html.Div(id='filter-container'),

                    # Tableau de données filtrées
                    dash_table.DataTable(
                        id='filtered-table',
                        columns=[{'name': col, 'id': col} for col in df.columns],
                        page_size=5,
                        style_table={'overflowX': 'auto'}
                    )
                ]),

                id="table-collapse",
                is_open=False  # Masqué par défaut
            ),

            dcc.Store(id='data-to-fit', data=None),
            dcc.Store(id='data-dataset', data=None),

            html.H4("Real time model fit", style={'textAlign': 'center', 'marginTop': '10px'}),

            html.Div([
                html.Label("Show", style={'marginRight': '10px'}),
                dcc.RadioItems(
                    id="radio-selection",
                    options=[
                        {'label': '  first', 'value': 'first'},
                        {'label': '  last', 'value': 'last'},
                        {'label': '  one every', 'value': 'every'}
                    ],
                    value='first',  # Valeur par défaut
                    inline=False,
                    style={'display': 'block', 'gap': '20px', 'padding': '15px'}
                ),
                dcc.Input(id="number-curves", type="number", value=15, step=1, debounce=True,
                          style={'width': '50px', 'textAlign': 'center'}),

                html.Label("values.", style={'marginLeft': '10px'}),

                daq.ToggleSwitch(id='toggle-switch', value=False, label="Show | Hide data series",
                                 labelPosition="top", style={'marginLeft': '30px'}),

                # html.H4("Normalize", style={'textAlign': 'center', 'marginTop': '20px'}),
                get_norm()

            ], style={'display': 'flex', 'alignItems': 'center', 'fontSize': '15px'}),

            html.Div([
                dcc.Graph(id='live-graph', style={'width': '100%', 'height': '500px'}),
                dcc.Interval(id='interval-update', interval=2000, n_intervals=10, disabled=True),
                # Mise à jour toutes les 2s
                dcc.Interval(id='interval', interval=5000, disabled=True),  # Interval de 5 secondes
                # Stocke l'historique de F et l'état de complétion
                dcc.Store(id='data-store', data={'F_values': [], 'done': False, 'last_summary': None}),
            ], style={'textAlign': 'center', 'padding': '20px'}),

            dcc.Checklist(
                id='series-checklist',
                options=[],  # Options dynamiques
                value=[],  # Séries sélectionnées à afficher
                inline=True,
                style={'display': 'flex', 'gap': '30px', 'marginLeft': '70px', 'fontSize': '15px'}
            ),

            html.Div([
                html.Label("Import series from csv files: ",
                           style={'padding': '20px', 'alignItems': 'left', }),

                # ✅ Drag & Drop Box
                dcc.Upload(
                    id='upload-data',
                    children=[
                        html.Div([
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
                                    # 'marginRight': '20px'  # 🔥 Espace entre la box et le bouton
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
                    ],
                    multiple=True,
                    style={
                        'display': 'flex', 'width': '400px', 'justifyContent': 'left', 'alignItems': 'center'}
                ),

            ], style={
                'display': 'flex', 'justifyContent': 'left', 'alignItems': 'center', 'marginBottom': '20px'
            }),

            dcc.Dropdown(
                id='data-fit-selector',
                value='data',
                options=['data'],
                clearable=False,
            ),

            dcc.Store(id='csv-series', data={}),

            dcc.Store(id='normalization'),

            dcc.Store(id='selected-data-name'),

            get_menu(),

            html.H5("Data selected", style={'textAlign': 'center', 'padding': '10px'}),
            dash_table.DataTable(
                id='data-params',
                columns=[{'name': col, 'id': col} for col in df.columns],
                page_size=5,
                style_table={'overflowX': 'auto'}
            ),
        ])
