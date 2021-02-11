import dash_html_components as html
import dash_bootstrap_components as dbc

import utils

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Channels: "))]),
        dbc.Row([dbc.Col(html.H6(id='h6_channel_string_configuration', children=utils.string_channels()), className="mb-4")]),
        dbc.Row([
            dbc.Col(dbc.Card(children=[html.H3(children='Access the code',
                                               className="text-center"),
                                       dbc.Button("GitHub",
                                                  href="https://github.com/Teslassian/SigfoxAWS",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True),
                    width=4, className="mb-4"),

            dbc.Col(dbc.Card(children=[html.H3(children='Access the data',
                                               className="text-center"),
                                       dbc.Button("AWS",
                                                  href="https://console.aws.amazon.com/dynamodb/home?region=us-east-1#tables:",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True),
                width=4, className="mb-4"),

            dbc.Col(dbc.Card(children=[html.H3(children='Access the backend',
                                               className="text-center"),
                                       dbc.Button("Sigfox",
                                                  href="https://backend.sigfox.com/device/list",
                                                  color="primary",
                                                  className="mt-3"),
                                       ],
                             body=True, color="dark", outline=True),
                    width=4, className="mb-4"),
        ], className="mb-5"),

    ])

])
