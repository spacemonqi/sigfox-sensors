import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import channels
from app import app
import callbacks

##################################################
# try to change the direct downlink data in the sigfox backend from here! then a server wont be needed for downlinks
##################################################

channel_ld = channels.get_channels()

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Selected Channels: "))]),
        dbc.Row([dbc.Col(html.H6(id='h6_channel_string_configuration', children=channels.string_channels()), className="mb-4")]),
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Channel Configuration', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),
        dbc.Row([
                dbc.Col(width = 2),
                dbc.Col(children=[html.P('''Channel Alias:''')], width = 4),
                dbc.Col(children=[html.P('''Scaling Factor:''')], width = 4),
                html.Div(id="output"),
        ]),

        html.Div(id='placeholder_update'),
        dbc.Row([
                dbc.Col(html.H4('''Channel 1:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_1",
                                  type="text",
                                  placeholder = channel_ld[0]['alias'],
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_1",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 2:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_2",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_2",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 3:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_3",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_3",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 4:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_4",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_4",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 5:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_5",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_5",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 6:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_6",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_6",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '325px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ])

    ])
])

# Callback function to update the placeholders in the inputs
@app.callback([Output("in_alias_1", "placeholder"),
               Output("in_scaling_factor_1", "placeholder"),
               Output("in_alias_2", "placeholder"),
               Output("in_scaling_factor_2", "placeholder"),
               Output("in_alias_3", "placeholder"),
               Output("in_scaling_factor_3", "placeholder"),
               Output("in_alias_4", "placeholder"),
               Output("in_scaling_factor_4", "placeholder"),
               Output("in_alias_5", "placeholder"),
               Output("in_scaling_factor_5", "placeholder"),
               Output("in_alias_6", "placeholder"),
               Output("in_scaling_factor_6", "placeholder")],
              Input("placeholder_update", "children"))
def update_output(x):

    channels_ld = channels.get_channels()
    placeholder_list = []

    for dict in channels_ld:
        placeholder_list.append(dict['alias'])
        placeholder_list.append(dict['scaling_fact'])

    return placeholder_list
