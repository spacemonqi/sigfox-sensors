import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import utils

df = utils.get_df('../data/sensor_data.csv')
channel_ld = utils.get_channels()

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network - Downlink"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Channels: "))]),
        dbc.Row([dbc.Col(html.H6(id='h6_channel_string_configuration', children=utils.string_channels()), className="mb-4")]),

        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Time Calibration', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),
        dbc.Row([
                dbc.Col(width = 2),
                dbc.Col(children=[html.P('''Device ID:''')], width = 4),
                dbc.Col(children=[html.P('''tai:''')], width = 4),
        ]),
        dbc.Row([
            dbc.Col(html.H4('''Devices:'''), width = 2),
            dbc.Col(
                dcc.Dropdown(
                    id='dd_id_tai',
                    options=utils.get_options(df['deviceId'].unique()),
                    style={'width': '200px',
                           'height': '35px',
                           'display': 'inline-block',
                           'margin-bottom': '10px',
                           'color': 'black',
                           'background-color': 'white'}
                ),
                width = 4,
            ),
            dbc.Col(
                dcc.Input(
                    id="in_tai",
                    type="text",
                    placeholder = "",
                    style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                ),
                width = 4,
            ),
        ]),

        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Sampling Frequency', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),
        dbc.Row([
                dbc.Col(width = 2),
                dbc.Col(children=[html.P('''Device ID:''')], width = 4),
                dbc.Col(children=[html.P('''sf:''')], width = 4),
        ]),
        dbc.Row([
            dbc.Col(html.H4('''Devices:'''), width = 2),
            dbc.Col(
                dcc.Dropdown(
                    id='dd_id_sf',
                    options=utils.get_options(df['deviceId'].unique()),
                    style={'width': '200px',
                           'height': '35px',
                           'display': 'inline-block',
                           'margin-bottom': '10px',
                           'color': 'black',
                           'background-color': 'white'}
                ),
                width = 4,
            ),
            dbc.Col(
                dcc.Input(
                    id="in_sf",
                    type="text",
                    placeholder = "",
                    style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                ),
                width = 4,
            ),
        ]),

        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Downlink Frequency', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),
        dbc.Row([
                dbc.Col(width = 2),
                dbc.Col(children=[html.P('''Device ID:''')], width = 4),
                dbc.Col(children=[html.P('''df:''')], width = 4),
        ]),
        dbc.Row([
            dbc.Col(html.H4('''Devices:'''), width = 2),
            dbc.Col(
                dcc.Dropdown(
                    id='dd_id_df',
                    options=utils.get_options(df['deviceId'].unique()),
                    style={'width': '200px',
                           'height': '35px',
                           'display': 'inline-block',
                           'margin-bottom': '10px',
                           'color': 'black',
                           'background-color': 'white'}
                ),
                width = 4,
            ),
            dbc.Col(
                dcc.Input(
                    id="in_df",
                    type="text",
                    placeholder = "",
                    style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                ),
                width = 4,
            ),
        ]),
    ])
])
