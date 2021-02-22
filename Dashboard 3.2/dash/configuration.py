import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import utils
from app import app

########################################################################################################################
# try to change the direct downlink data in the sigfox backend from here! then a server wont be needed for downlinks
########################################################################################################################

df = utils.get_df('../data/sensor_data.csv')
channel_ld = utils.get_channels()

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network - Configuration"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Channels: "))]),
        dbc.Row([dbc.Col(html.H6(id='h6_channel_string', children=utils.string_channels()), className="mb-4")]),
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Channel Configuration', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),
        dbc.Row([
                dbc.Col(width = 2),
                dbc.Col(children=[html.P('''Channel Alias:''')], width = 4),
                dbc.Col(children=[html.P('''Scaling Factor:''')], width = 4),
        ]),

        dbc.Row([
                dbc.Col(html.H4('''Channel 1:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_1",
                                  type="text",
                                  placeholder = channel_ld[0]['alias'],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_1",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 2:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_2",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_2",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 3:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_3",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_3",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 4:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_4",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_4",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 5:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_5",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_5",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),
        dbc.Row([
                dbc.Col(html.H4('''Channel 6:'''), width = 2),
                dbc.Col(dcc.Input(id="in_alias_6",
                                  type="text",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
                dbc.Col(dcc.Input(id="in_scaling_factor_6",
                                  type="number",
                                  placeholder = "",
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width = 4,
                ),
        ]),

        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Device Configuration', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),
        dbc.Row([
                dbc.Col(width = 2),
                dbc.Col(children=[html.P('''Device ID:''')], width = 4),
                dbc.Col(children=[html.P('''Device Alias:''')], width = 4),
        ]),
        dbc.Row([
            dbc.Col(html.H4('''Devices:'''), width = 2),
            dbc.Col(
                dcc.Dropdown(
                    id='dd_id',
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
                    id="in_device_alias",
                    type="text",
                    placeholder = "",
                    style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                ),
                width = 4,
            ),
        ]),
    ])
])

# Callback function to update placeholders in the inputs
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
               Output("in_scaling_factor_6", "placeholder"),
               Output("in_device_alias", "value")],
              [Input("dd_id", "value")])
def placeholders_update(deviceid):

    if deviceid:
        with open('temp/dd_current_devid.txt', mode='w') as file:
            file.write(deviceid)
            file.close()

    channels_ld = utils.get_channels()
    devices_ld = utils.get_devices()

    placeholder_list = []

    for dict in channels_ld:
        placeholder_list.append(dict['alias'])
        placeholder_list.append(dict['scaling_fact'])

    flag = False
    for dict in devices_ld:
        if dict['name'] == deviceid:
            placeholder_list.append(dict['alias'])
            flag = True
    if not flag:
        placeholder_list.append("")

    return placeholder_list

# Callback function to write device aliases to csv
@app.callback(Output("in_device_alias", "type"),
              Input("in_device_alias", "value"))
def device_alias_update(new_alias):

    with open('config/dd_current_devid.txt', mode='r') as file:
        deviceid = file.read()
        file.close()

    devices_ld = utils.get_devices()

    if new_alias:
        for i in range(len(devices_ld)):
            if devices_ld[i]['name'] == deviceid:
                devices_ld[i]['alias'] = new_alias

    utils.update_devices(devices_ld)

    return 'text'

# Callback function to update the channel aliases and scaling factors
@app.callback(Output("h6_channel_string", "children"),
              [Input("in_alias_1", "value"),
              Input("in_scaling_factor_1", "value"),
              Input("in_alias_2", "value"),
              Input("in_scaling_factor_2", "value"),
              Input("in_alias_3", "value"),
              Input("in_scaling_factor_3", "value"),
              Input("in_alias_4", "value"),
              Input("in_scaling_factor_4", "value"),
              Input("in_alias_5", "value"),
              Input("in_scaling_factor_5", "value"),
              Input("in_alias_6", "value"),
              Input("in_scaling_factor_6", "value")])
def update_channel_string(a1, s1, a2, s2, a3, s3, a4, s4, a5, s5, a6, s6):

    channels_ld = utils.get_channels()

    if a1: channels_ld[0]['alias'] = a1
    if a2: channels_ld[1]['alias'] = a2
    if a3: channels_ld[2]['alias'] = a3
    if a4: channels_ld[3]['alias'] = a4
    if a5: channels_ld[4]['alias'] = a5
    if a6: channels_ld[5]['alias'] = a6

    if s1: channels_ld[0]['scaling_fact'] = float(s1)
    if s2: channels_ld[1]['scaling_fact'] = float(s2)
    if s3: channels_ld[2]['scaling_fact'] = float(s3)
    if s4: channels_ld[3]['scaling_fact'] = float(s4)
    if s5: channels_ld[4]['scaling_fact'] = float(s5)
    if s6: channels_ld[5]['scaling_fact'] = float(s6)

    utils.update_channels(channels_ld)

    channel_name_string = utils.string_channels()

    return channel_name_string
