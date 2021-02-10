import dash_html_components as html
import dash_bootstrap_components as dbc

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([
            dbc.Col(dbc.Card(children=[html.H3(children='Access the code',
                                               className="text-center"),
                                       dbc.Button("GitHub",
                                                  href="https://github.com",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True),
                    width=4, className="mb-4"),

            dbc.Col(dbc.Card(children=[html.H3(children='Access the data',
                                               className="text-center"),
                                       dbc.Button("GitHub",
                                                  href="https://github.com",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True),
                width=4, className="mb-4"),

            dbc.Col(dbc.Card(children=[html.H3(children='Access the repo',
                                               className="text-center"),
                                       dbc.Button("GitHub",
                                                  href="https://github.com",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True),
                    width=4, className="mb-4"),
        ], className="mb-5"),

    ])

])
