#Imports=========================================================================================================================#
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_useful_components as duc
import pandas as pd
import numpy as np
from app import app
import utils
# bruh



#Global==========================================================================================================================#
colorlist = ['#FF4F00', '#FFF400', '#FF0056', "#5E0DAC", '#60AAED', '#1CA776']



#Data============================================================================================================================#
df = utils.get_df('../data/sensor_data.csv')
locations_ld = utils.get_locations()
devices_ld = utils.get_devices()
channels_ld = utils.get_channels()
checkboxtree_nodes = utils.checkboxtree_nodes(locations_ld, devices_ld, channels_ld)



#Layout Components===============================================================================================================#
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row([
                        dbc.Col(html.Img(src="/assets/divigraph.png", height="40px"), width=1, align="center"),
                        dbc.Col(dbc.NavbarBrand("Divigraph", className="ml-2"), width=1, align="center"),
                        ],
                        align="center",
                        no_gutters=True,
                ),
                href="/monitoring",
            ),
        ],
        fluid = True
    ),
    color="primary",
    dark=True,
    className="mb-4",
)

body_left_card_tree = dbc.CardBody(
    [
        dbc.Row(html.Div(duc.CheckBoxTree(
                            id="nav_tree",
                            nodes=checkboxtree_nodes,
                            disabled = False,
                            expandDisabled = False,
                            expandOnClick = True,
                            noCascade = True,
                            onlyLeafCheckboxes = False,
                            optimisticToggle = True,
                            showNodeIcon = False,
                        )), className='mb-2'),
        dbc.Row(html.Div(id='checked-output'), className='mb-4'),
        dbc.Row(html.Div(id='expanded-output'), className='mb-4'),
    ],
    style = {'color': 'white'}
),

body_right_metrics_right = html.Div([
    dbc.Button('Run', id='btn_pause', color='primary'),
    dbc.Card(
        children = [
            dbc.CardHeader(children=["Device <devid>"]),
            dbc.CardBody(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Name', addon_type="prepend"),
                            dbc.Input(placeholder=""),
                        ],
                        className="mb-2",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('@', addon_type="prepend"),
                            dbc.Input(placeholder=""),
                        ],
                        className="mb-2",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('@', addon_type="prepend"),
                            dbc.Input(placeholder=""),
                        ],
                        className="mb-2",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('@', addon_type="prepend"),
                            dbc.Input(placeholder=""),
                        ],
                        className="mb-2",
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('@', addon_type="prepend"),
                            dbc.Input(placeholder=""),
                        ],
                        className="mb-2",
                    ),
                ],
            )
        ],
        color='primary'
    )
])

# table_header = [html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))]
# row1 = html.Tr([html.Td("Arthur"), html.Td("Dent")])
# row2 = html.Tr([html.Td("Ford"), html.Td("Prefect")])
# row3 = html.Tr([html.Td("Zaphod"), html.Td("Beeblebrox")])
# row4 = html.Tr([html.Td("Trillian"), html.Td("Astra")])
# table_body = [html.Tbody([row1, row2, row3, row4])]
# table = dbc.Table(table_header + table_body, bordered=True)
# graph_ch1 = dbc.Card(
#     [
#         dbc.Row([
#             dbc.Col([dcc.Graph(id='graph_ch1', animate=True, style={'display': 'none'})], width=6),
#             dbc.Col(table, width=6)
#         ])
#     ],
#     color="primary", className='mb-1'
# )
graph_ch1 = dbc.Card(dcc.Graph(id='graph_ch1', animate=True, style={'display': 'none'}), color="primary", className='mb-1')
graph_ch2 = dbc.Card(dcc.Graph(id='graph_ch2', animate=True, style={'display': 'none'}), color="primary", className='mb-1')
graph_ch3 = dbc.Card(dcc.Graph(id='graph_ch3', animate=True, style={'display': 'none'}), color="primary", className='mb-1')
graph_ch4 = dbc.Card(dcc.Graph(id='graph_ch4', animate=True, style={'display': 'none'}), color="primary", className='mb-1')
graph_ch5 = dbc.Card(dcc.Graph(id='graph_ch5', animate=True, style={'display': 'none'}), color="primary", className='mb-1')
graph_ch6 = dbc.Card(dcc.Graph(id='graph_ch6', animate=True, style={'display': 'none'}), color="primary", className='mb-1')



#Layout Divisions================================================================================================================#
DIV_body_right_channels = html.Div(
    id='DIV_body_right_channels',
    children = [
        graph_ch1,
        graph_ch2,
        graph_ch3,
        graph_ch4,
        graph_ch5,
        graph_ch6,
        # dbc.Row([
        #     dbc.Col(graph_ch1, width=6),
        #     dbc.Col(graph_ch2, width=6),
        # ]),
        # dbc.Row([
        #     dbc.Col(graph_ch3, width=6),
        #     dbc.Col(graph_ch4, width=6),
        # ]),
        # dbc.Row([
        #     dbc.Col(graph_ch5, width=6),
        #     dbc.Col(graph_ch6, width=6),
        # ]),
    ]
)

DIV_body_right_devices = html.Div(
    dbc.Container([
        dbc.Row([dbc.Col(dbc.Card(html.H3(id='ch_config', children='Channel Configuration', className="text-center bg-primary"),
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
                                  placeholder = channels_ld[0]['alias'],
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
)

DIV_body_right_locations = html.Div()

DIV_body_right_none = html.Div()



#Layout==========================================================================================================================#
layout = html.Div([
    dbc.Container(
        [
            dbc.Row(  # Row for body
                [
                    dcc.Interval(id='graph_update', interval= 2*1000, n_intervals=0),
                    dbc.Col(  # Col for body_left
                        [
                            dbc.Card(body_left_card_tree, color="primary", style={'height': '100%'})
                        ],
                        style={"height": "90%"},
                        width = 2
                    ),
                    dbc.Col(  # Col for body_right
                        id = 'col_body_right',
                        children = DIV_body_right_channels,
                        width = 10,
                    )
                ],
                className="h-100",
            )
        ],
        style={"height": "100vh"},
        fluid=True
    )
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', children=layout)
])



#Graphing========================================================================================================================#
# Pause live updates
@app.callback([Output("graph_update", "interval"),
               Output("btn_pause", "children")],
              [Input("btn_pause", "n_clicks"),
               Input("btn_pause", "children")])
def on_button_click(n, current):
    if current == 'Pause':
        return [1000*1000, 'Run']
    else:
        return [2*1000, 'Pause']

# Apply scaling factors and update the graphs
@app.callback([Output('graph_ch1', 'figure'),
               Output('graph_ch2', 'figure'),
               Output('graph_ch3', 'figure'),
               Output('graph_ch4', 'figure'),
               Output('graph_ch5', 'figure'),
               Output('graph_ch6', 'figure')],
              [Input('graph_update', 'n_intervals'),
               Input('nav_tree', 'checked')])
def update_graphs(n, checked):

    channels_ld = utils.get_channels()
    scaling_fact = 1.0
    df_scaled = pd.read_csv('../data/sensor_data.csv')
    df_scaled['value'] = df_scaled['value'].astype(float)
    df_scaled['change'] = df_scaled['change'].astype(float)
    for dict in channels_ld:
        channel = dict['name']
        scaling_fact = float(dict['scaling_fact'])
        df_scaled.loc[df_scaled['data']==channel, 'value'] = df_scaled[df_scaled['data']==channel]['value'] * scaling_fact
        df_scaled.loc[df_scaled['data']==channel, 'change'] = df_scaled[df_scaled['data']==channel]['change'] * scaling_fact
    df_scaled.index = pd.to_datetime(df_scaled['timestamp'])  # remove this, make the graph read directly from the timestamp column if possible

    figures = []
    i = 0
    for channel in channels_ld:

        trace = []

        if checked:
            device = checked[0].split('_')[1][3:]
            df_data = df_scaled[df_scaled['data'] == channel['name']]
            df_data_id = df_data[df_data['deviceId'] == device]
            xmin = df_data_id.index.min()
            xmax = df_data_id.index.max()
            ymin = df_data_id['value'].min() - 0.05 * np.abs(df_data_id['value'].max())
            ymax = df_data_id['value'].max() + 0.05 * np.abs(df_data_id['value'].max())
            trace.append(go.Scatter(x=df_data_id.index,
                                    y=df_data_id['value'],
                                    mode='lines+markers',
                                    line={'width': 3},
                                    opacity=0.7,
                                    name=device,
                                    textposition='bottom center',
                                    # fill='tozeroy'
                        )
            )
        else:
            df_clear = df_scaled
            df_clear['value'].values[:] = 0
            xmin = df_scaled.index.min()
            xmax = df_scaled.index.max()
            ymin = -100
            ymax = 100
            trace.append(go.Scatter(x=df_clear.index,
                                    y=df_clear['value'],
                                    mode='lines',
                                    line={'width': 3},
                                    opacity=0.7,
                                    textposition='bottom center'
                        )
            )

        traces = [trace]
        data = [val for sublist in traces for val in sublist]

        # print('\n\n')
        # print(channel)
        # print(data[0]['x'])

        figure = {'data': data,
                  'layout': go.Layout(
                      colorway=colorlist,
                      template='plotly_dark',
                      paper_bgcolor='rgba(0, 0, 0, 0)',
                      plot_bgcolor='rgba(0, 0, 0, 0)',
                      hovermode='x',
                      autosize=True,
                      margin={'t': 50, 'l': 50, 'b': 10, 'r': 20},
                      title={'text': channels_ld[i]['alias'], 'font': {'color': 'white'}, 'x': 0.5},
                      xaxis={'range': [xmin, xmax], 'gridcolor': 'white', 'gridwidth': 0.5},
                      yaxis={'range': [ymin, ymax], 'gridcolor': 'white'},
                  ),
                  }

        figures.append(figure)

        i += 1

    return figures

# Show/Hide Graphs
@app.callback([Output('graph_ch1', 'style'),
               Output('graph_ch2', 'style'),
               Output('graph_ch3', 'style'),
               Output('graph_ch4', 'style'),
               Output('graph_ch5', 'style'),
               Output('graph_ch6', 'style')],
              Input('nav_tree', 'checked'))
def display_graphs(checked):

    channels = []
    channels_ld = utils.get_channels()
    graphs_to_display = []

    if checked:
        for item in checked:
            substrings = item.split('_')
            channels.append(substrings[2])

    for channel_dict in channels_ld:
        if channel_dict['name'] in channels:
            graphs_to_display.append({})
        else:
            graphs_to_display.append({'display': 'none'})

    return graphs_to_display

# # Update graph_timeseries based on the dropdown
# @app.callback(Output('graph_timeseries', 'figure'),
#               [Input('dd_id', 'value'),
#                Input('dd_channel', 'value'),
#                Input('graph_update', 'n_intervals')])
# def update_graph_timeseries(ids, data, n):
#
#     df = pd.read_csv('../data/sensor_data_scaled.csv', parse_dates=True)
#     df.index = pd.to_datetime(df['timestamp'])  # remove this, make the graph read directly from the timestamp column if possible
#
#     trace = []
#
#     if ids and data:
#         df_data = df[df['data'] == data]
#         xmin = df_data.index.min()
#         xmax = df_data.index.max()
#         ymin = df_data['value'].min() - 0.05 * np.abs(df_data['value'].max())
#         ymax = df_data['value'].max() + 0.05 * np.abs(df_data['value'].max())
#         for id in ids:
#             df_data_id = df_data[df_data['deviceId'] == id]
#             trace.append(go.Scatter(x=df_data_id.index,
#                                     y=df_data_id['value'],
#                                     mode='lines+markers',
#                                     opacity=0.7,
#                                     line={'width': 3},
#                                     name=id,
#                                     textposition='bottom center'))
#     else:
#         df_clear = df
#         df_clear['value'].values[:] = 0
#         xmin = df.index.min()
#         xmax = df.index.max()
#         ymin = -100
#         ymax = 100
#         trace.append(go.Scatter(x=df_clear.index,
#                                 y=df_clear['value'],
#                                 mode='lines',
#                                 opacity=0.7,
#                                 line={'width': 3},
#                                 textposition='bottom center'
#                     )
#         )
#
#     traces = [trace]
#     data = [val for sublist in traces for val in sublist]
#
#     figure = {'data': data,
#               'layout': go.Layout(
#                   colorway=colorlist,
#                   template='plotly_dark',
#                   paper_bgcolor='rgba(0, 0, 0, 0)',
#                   plot_bgcolor='rgba(0, 0, 0, 0)',
#                   hovermode='x',
#                   height=500,
#                   autosize=True,
#                   title={'text': 'Sensor Data', 'font': {'color': 'white'}, 'x': 0.5},
#                   xaxis={'range': [xmin, xmax], 'gridcolor': 'white', 'gridwidth': 0.5},
#                   yaxis={'range': [ymin, ymax], 'gridcolor': 'white'},
#               ),
#     }
#
#     return figure



#Structure=======================================================================================================================#
# Switch between views
@app.callback([Output('nav_tree', 'checked'),
               Output('col_body_right', 'children')],
              Input('nav_tree', 'checked'))
def switch_views(checked):

    if checked is None:
        checked = []

    # print('\nchecked')
    # print(checked)

    with open('temp/tree.txt', 'r') as filehandle:
        checked_global = [current_place.rstrip() for current_place in filehandle.readlines()]
    # print('\nchecked_global')
    # print(checked_global)

    checked_diff = list(set(checked).difference(checked_global))
    # print('\nchecked_diff')
    # print(checked_diff)

    if not checked:
        checked_global = checked
    elif not checked_global:
        checked_global = checked
    elif not checked_diff:
        checked_global = checked
    elif (checked_global[0].find('CH') > -1) and (checked_diff[0].find('CH') > -1):
        checked_global = checked
    else:
        checked_global = checked_diff

    with open('temp/tree.txt', 'w') as filehandle:
        filehandle.writelines("%s\n" % item for item in checked_global)

    # print('\nchecked_global')
    # print(checked_global)

    if checked_global:
        if checked_global[0].find('CH') > -1:
            return checked_global, DIV_body_right_channels

        if checked_global[0].find('dev') > -1:
            return checked_global, DIV_body_right_devices

        if checked_global[0].find('loc') > -1:
            return checked_global, DIV_body_right_locations

    return checked_global, DIV_body_right_none



#Devices=========================================================================================================================#
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
def update_device_config(new_alias):

    with open('temp/dd_current_devid.txt', mode='r') as file:
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
@app.callback(Output("ch_config", "children"),
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
def update_channel_config(a1, s1, a2, s2, a3, s3, a4, s4, a5, s5, a6, s6):

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

    # channel_name_string = utils.string_channels()

    return 'Channel Configuration'



#Main============================================================================================================================#
if __name__ == '__main__':
    # app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)
    app.run_server(debug=True)
