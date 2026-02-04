# layouts/layout_left_panel.py
from dash import html, dcc
import dash_bootstrap_components as dbc
import tools as pt


def get_left_panel(eq_system, x_pars, fixed_pars, variable_pars, pfd_pars, fluo_eq, latex):
    return html.Div(style={'width': '40%', 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}, children=[
                # System
                html.Div(style={'width': '100%', 'padding': '10px', 'position': 'relative'},
                         children=[
                             html.H4("System", style={'textAlign': 'center'}),
                             dcc.Textarea(
                                 id='system-input',
                                 placeholder="Enter an equation system",
                                 value=eq_system,
                                 style={'width': '100%', 'height': '170px', "white-space": "pre-wrap"}

                             ),

                             html.Div(
                                 id='x-container',
                                 children=[
                                     html.Div([
                                         dcc.Markdown(f'$${pt.elem_to_latex(var) + " ="}$$', mathjax=True,
                                                      style={'marginTop': '10px', 'marginLeft': '10px'}),
                                         dbc.Input(value=value, placeholder="Enter value",
                                                   id={'type': 'x-value', 'index': i},
                                                   style={'width': '80px', 'marginLeft': '10px'}),
                                     ], style={'marginBottom': '0px', 'display': 'flex', 'alignItems': 'center'})
                                     for i, (var, value) in enumerate(x_pars.items())
                                 ],
                                 style={'display': 'flex', 'width': '100%', 'flexWrap': 'wrap'}
                             ),

                             html.Button("Get params", id='get-params', className='btn btn-primary', style={
                                 'width': '100%', 'backgroundColor': '#2c70d6', 'color': 'white', 'fontWeight': 'bold',
                                 'marginTop': '10px'
                             }),
                             html.Div([
                                 html.I(id="valid-icon"),

                             ], style={'position': 'absolute', 'top': '55px', 'right': '20px', 'zIndex': '10'},
                                 className="tooltip-container"),
                         ]),

                html.Div(id='latex-system', style={'width': '100%', 'marginLeft': '15px', 'position': 'relative'},
                         children=[
                             html.Div([
                                 # ✅ Icône d'information (cliquable)
                                 html.I(id="info-icon", className="fa-solid fa-info-circle",
                                        style={"fontSize": "24px", "color": "blue"}),

                                 # ✅ Info-bulle qui s'affiche au survol
                                 dbc.Tooltip(['To avoid LateX rendering issues in screenshot:', html.Br(),
                                              'Right-click on LateX equation > "Accessibility" > Deactivate "Include Hidden MathML"'],
                                             target="info-icon", placement="right"),

                             ], style={'position': 'absolute', 'top': '5px', 'right': '30px', 'zIndex': '10'},
                                 className="tooltip-container"),

                             html.Div(id='latex-container', children=[
                                 html.Div([
                                     dcc.Markdown(
                                         f'$${eq}$$',
                                         mathjax=True
                                     ),
                                 ])
                                 for eq in latex
                             ]),
                         ]),

                html.Div(style={
                    'display': 'flex',
                    'width': '100%',
                    'justifyContent': 'flex-start',
                    'flexWrap': 'wrap',
                    'gap': '0px'
                }, children=[

                    # Fixed params
                    html.Div(style={'width': '50%'}, children=[
                        html.H4("Fixed params", style={'textAlign': 'center', 'marginLeft': '10px'}),
                        html.Div(id='fixed-params-container', children=[
                            html.Div([
                                dbc.Input(value=var, type="text", disabled=True, style={'width': '45%'}),
                                dbc.Input(value=value, placeholder="Enter value",
                                          id={'type': 'fixed-param-value', 'index': i},
                                          style={'width': '45%', 'marginLeft': '10px'}),
                            ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center',
                                      'marginLeft': '10px'})
                            for i, (var, value) in enumerate(fixed_pars.items())
                        ]),
                    ]),

                    # Variable params
                    html.Div(style={'width': '50%'}, children=[
                        html.H4("Variable params", style={'textAlign': 'center'}),
                        html.Div(id='variable-params-container', children=[
                            html.Div([
                                dbc.Input(value=var, type="text", disabled=True, style={'width': '45%'}),
                                dbc.Input(value=value, placeholder="Enter value",
                                          id={'type': 'variable-param-value', 'index': i},
                                          style={'width': '45%', 'marginLeft': '10px'}),
                            ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center'})
                            for i, (var, value) in enumerate(variable_pars.items())
                        ]),

                        html.H4("PFD Definition", style={'textAlign': 'center', 'marginTop': '20px'}),
                        html.Div(id='pfd-container', children=[
                            html.Div([
                                dbc.Input(value=var, type="text", disabled=True,
                                          style={'width': '45%', 'marginLeft': '10px'}),
                                dbc.Input(value=value, placeholder="Enter value",
                                          id={'type': 'pfd-value', 'index': i},
                                          style={'width': '45%', 'marginLeft': '10px'}),
                            ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center'})
                            for i, (var, value) in enumerate(pfd_pars.items())
                        ]),

                        # Fluo Definition
                        html.H4("Fluo Definition", style={'textAlign': 'center', 'marginTop': '20px'}),
                        dcc.Textarea(
                            id='fluo-input',
                            placeholder="Enter a fluorescence equation",
                            value=fluo_eq,
                            style={'width': '95%', 'height': '40px', 'marginLeft': '10px'}
                        ),

                    ]),

                ]),
            ])
