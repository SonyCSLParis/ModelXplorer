from dash import html, dcc


def get_norm():
    return html.Div(style={'display': 'flex', 'width': "400px", "marginLeft": "20px"}, children=[
                "Normalize: ",
                html.Div(style={'width': '30%', 'marginLeft': '20px'}, children=[

                    dcc.RadioItems(
                        id="norm-type",
                        options=[
                            {'label': '  divisive', 'value': 'div'},
                            {'label': '  substractive', 'value': 'sub'},
                        ],
                        value='div',  # Valeur par défaut
                        inline=False,
                        style={'gap': '30px'}
                    ),
                ]),

                html.Div(style={'width': '20%', 'marginLeft': '10px'}, children=[
                    dcc.RadioItems(
                        id="norm-mean",
                        options=[
                            {'label': '  mean', 'value': 'mean'},
                            {'label': '  index', 'value': 'index'},
                        ],
                        value='mean',  # Valeur par défaut
                        inline=False,
                        style={'gap': '30px'}
                    ),
                ]),

                html.Div(style={'width': '20%', 'marginLeft': '20px', 'marginTop': '20px'}, children=[
                    dcc.Input(
                        id="norm-value",
                        type="number",
                        value=0,
                        style={"display": "none", "marginLeft": "10px", "width": "50px"}
                    )
                ])
            ])
