#Imports=========================================================================================================================#
# All callbacks should take nav_tree checked as input to force them to update on page change



#Imports=========================================================================================================================#
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_useful_components as duc
import dash
import pandas as pd
import numpy as np
from app import app
import utils
import glob
import os



#Global==========================================================================================================================#
colorlist = ['#FF4F00', '#FFF400', '#FF0056', '#5E0DAC', '#60AAED', '#1CA776']

disabled_dict = {'Enabled': False, 'Disabled': True}

data_locations = pd.read_csv("../data/data_locations.csv")
fig_map = px.scatter_mapbox(data_locations, lat="lat", lon="lon", hover_name="deviceid", hover_data=["state"],
                            color_discrete_sequence=["#FF4F00"], zoom=14, height=950)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
map = dbc.Card(dcc.Graph(id='graph_map', animate=True, figure=fig_map), color='primary', className='mb-1')



#Data============================================================================================================================#
df = utils.get_df('../data/sensor_data.csv')
locations_ld = utils.get_locations()
devices_ld = utils.get_devices()
channels_ld = utils.get_channels()
tree_nodes = utils.update_tree_nodes(locations_ld, devices_ld, channels_ld)



#Layout Components===============================================================================================================#
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row([
                        dbc.Col(html.Img(src='/assets/divigraph.png', height='40px'), width=1, align='center'),
                        dbc.Col(dbc.NavbarBrand('Divigraph', className='ml-2'), width=1, align='center'),
                        ],
                        align='center',
                        no_gutters=True,
                ),
                href='/monitoring',
            ),
        ],
        fluid = True
    ),
    color='primary',
    dark=True,
    className='mb-4',
)

body_left_card_tree = dbc.CardBody(
    [
        dbc.Row(html.Div(duc.CheckBoxTree(
                            id='nav_tree',
                            nodes=tree_nodes,
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
    dbc.Card(
        children = [
            dbc.CardBody(
                [
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Device ID', addon_type='prepend'),
                            dbc.Input(value='22229D7'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Device Type', addon_type='prepend'),
                            dbc.Input(value='Dev Kit'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Time', addon_type='prepend'),
                            dbc.Input(value=str(datetime.now().time())),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('SeqNumber', addon_type='prepend'),
                            dbc.Input(value='Engaged'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('LQI', addon_type='prepend'),
                            dbc.Input(value='Good'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Sampling Rate', addon_type='prepend'),
                            dbc.Input(value='1/day'),
                        ],
                        className='mb-2',
                    ),
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon('Battery', addon_type='prepend'),
                            dbc.Input(value='100%'),
                        ],
                        className='mb-2',
                    ),
                ],
            )
        ],
        color='primary',
        style={'height': '452px'}
    )
])

graph_ch1 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='graph_ch1', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(body_right_metrics_right, width=4)
], id='row_graph_ch1', style={'display': 'none'})
graph_ch2 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='graph_ch2', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(body_right_metrics_right, width=4)
], id='row_graph_ch2', style={'display': 'none'})
graph_ch3 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='graph_ch3', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(body_right_metrics_right, width=4)
], id='row_graph_ch3', style={'display': 'none'})
graph_ch4 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='graph_ch4', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(body_right_metrics_right, width=4)
], id='row_graph_ch4', style={'display': 'none'})
graph_ch5 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='graph_ch5', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(body_right_metrics_right, width=4)
], id='row_graph_ch5', style={'display': 'none'})
graph_ch6 = dbc.Row([
    dbc.Col(dbc.Card(dcc.Graph(id='graph_ch6', animate=True), color='primary', className='mb-1'), width=8),
    dbc.Col(body_right_metrics_right, width=4)
], id='row_graph_ch6', style={'display': 'none'})
# graph_ch1 = dbc.Card(dcc.Graph(id='graph_ch1', animate=True, style={'display': 'none'}), color='primary', className='mb-1')
# graph_ch2 = dbc.Card(dcc.Graph(id='graph_ch2', animate=True, style={'display': 'none'}), color='primary', className='mb-1')
# graph_ch3 = dbc.Card(dcc.Graph(id='graph_ch3', animate=True, style={'display': 'none'}), color='primary', className='mb-1')
# graph_ch4 = dbc.Card(dcc.Graph(id='graph_ch4', animate=True, style={'display': 'none'}), color='primary', className='mb-1')
# graph_ch5 = dbc.Card(dcc.Graph(id='graph_ch5', animate=True, style={'display': 'none'}), color='primary', className='mb-1')
# graph_ch6 = dbc.Card(dcc.Graph(id='graph_ch6', animate=True, style={'display': 'none'}), color='primary', className='mb-1')



#Layout Divisions================================================================================================================#
DIV_body_right_channels = html.Div(
    id='DIV_body_right_channels',
    children = [
        dbc.Card(
                dbc.Row([
                    dbc.Col(html.H3(children='Sensor Monitoring', className='text-center bg-primary mb-4', style = {'margin-top': '21px', 'margin-left': '3px'}), width=8),
                    dbc.Col(width=3),
                    dbc.Col(dbc.Button(children='Run', id='btn_pause', size='lg', color='primary', style={'margin-top': '17px'}), width=1)
                ]),
                color='primary',
                className='mb-1',
                # body=True,
        ),
        # dbc.Row(style={'height': '10px'}),
        # dbc.Row([
        #     dbc.Col(width=2),
        # ], style={'height': '50px'}),
        # dbc.Row([
        #     dbc.Col([
        html.Div(
            children = [
                dbc.Col([
                    graph_ch1,
                    graph_ch2,
                    graph_ch3,
                    graph_ch4,
                    graph_ch5,
                    graph_ch6,
                ]),
                # dbc.Col(body_right_metrics_right)
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
            ],
            style = {'maxHeight': '100vh', 'overflow': 'scroll'},
            className="no-scrollbars",
        )
        #     ], width=12)
        # ])
    ]
)

DIV_body_right_devices = html.Div(
    dbc.Container([
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Device Configuration', className='text-center bg-primary'),
                                  body=True,
                                  color='primary'),
                 className='mb-4')]),
        dbc.Row([
                dbc.Col(width=2),
                dbc.Col(children=[html.P('''Device Alias:''')], width=3),
        ]),
        dbc.Row([
            dbc.Col(html.H4(id='h4_device_id', children=['Device']), width=2),
            dbc.Col(
                dcc.Input(
                    id='in_alias_dev',
                    type='text',
                    placeholder = '',
                    style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                ),
                width=3,
            ),
        ]),

        dbc.Row([dbc.Col(dbc.Card(html.H3(id='ch_config', children='Channel Configuration', className='text-center bg-primary'),
                                  body=True,
                                  color='primary'),
                 className='mb-4')]),
        dbc.Row([
                dbc.Col(width=2),
                dbc.Col(children=[html.P('''Channel Alias:''')], width=3),
                dbc.Col(children=[html.P('''Scaling Factor:''')], width=3),
                dbc.Col(children=[html.P('''Unit:''')], width=2),
                dbc.Col(children=[html.P('''Enable/Disable:''')], width=2),
        ], no_gutters=True),
        dbc.Row([
                dbc.Col(html.H4('''Channel 1:'''), width=2),
                dbc.Col(dcc.Input(id='in_alias_ch1',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[0]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_sf_1',
                                  type='number',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[0]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_u_1',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[0]['disabled']],
                                  style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=2,
                ),
                dbc.Col(dbc.Button(id='btn_ch1', children=channels_ld[0]['disabled'], color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
                dbc.Col(html.H4('''Channel 2:'''), width=2),
                dbc.Col(dcc.Input(id='in_alias_ch2',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[1]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_sf_2',
                                  type='number',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[1]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_u_2',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[1]['disabled']],
                                  style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=2,
                ),
                dbc.Col(dbc.Button(id='btn_ch2', children=channels_ld[1]['disabled'], color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
                dbc.Col(html.H4('''Channel 3:'''), width=2),
                dbc.Col(dcc.Input(id='in_alias_ch3',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[2]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_sf_3',
                                  type='number',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[2]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_u_3',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[2]['disabled']],
                                  style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=2,
                ),
                dbc.Col(dbc.Button(id='btn_ch3', children=channels_ld[2]['disabled'], color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
                dbc.Col(html.H4('''Channel 4:'''), width=2),
                dbc.Col(dcc.Input(id='in_alias_ch4',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[3]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_sf_4',
                                  type='number',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[3]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_u_4',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[3]['disabled']],
                                  style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=2,
                ),
                dbc.Col(dbc.Button(id='btn_ch4', children=channels_ld[3]['disabled'], color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
                dbc.Col(html.H4('''Channel 5:'''), width=2),
                dbc.Col(dcc.Input(id='in_alias_ch5',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[4]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_sf_5',
                                  type='number',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[4]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_u_5',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[4]['disabled']],
                                  style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=2,
                ),
                dbc.Col(dbc.Button(id='btn_ch5', children=channels_ld[4]['disabled'], color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
        dbc.Row([
                dbc.Col(html.H4('''Channel 6:'''), width=2),
                dbc.Col(dcc.Input(id='in_alias_ch6',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[5]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_sf_6',
                                  type='number',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[5]['disabled']],
                                  style = {'width': '200px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=3,
                ),
                dbc.Col(dcc.Input(id='in_u_6',
                                  type='text',
                                  placeholder = '',
                                  disabled=disabled_dict[channels_ld[5]['disabled']],
                                  style = {'width': '120px', 'height': '35px', 'margin-bottom': '30px'}
                        ),
                        width=2,
                ),
                dbc.Col(dbc.Button(id='btn_ch6', children=channels_ld[5]['disabled'], color='primary', style={'height': '35px', 'width': '120px'}), width=2),
        ], no_gutters=True),
    ])
)

DIV_body_right_locations = html.Div(map)

DIV_body_right_none = html.Div()



#Layout==========================================================================================================================#
layout = html.Div([
    dbc.Container(
        [
            dbc.Row(  # Row for body
                [
                    dcc.Interval(id='graph_update', interval=1*1000, n_intervals=0),
                    dbc.Col(  # Col for body_left
                        [
                            dbc.Card(body_left_card_tree, color='primary', style={'height': '100%'})
                        ],
                        style={'height': '90%'},
                        width=2
                    ),
                    dbc.Col(  # Col for body_right
                        id = 'col_body_right',
                        children = DIV_body_right_channels,
                        width=10,
                    )
                ],
                className='h-100',
            )
        ],
        style={'height': '100vh'},
        fluid=True
    )
])

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        navbar,
        layout,
        # className="no-scrollbars",
    ]
)



#Graphing========================================================================================================================#
# Pause live updates
@app.callback([Output('graph_update', 'interval'),
               Output('btn_pause', 'children')],
              [Input('btn_pause', 'n_clicks'),
               Input('btn_pause', 'children')])
def on_button_click(n, current):
    if current == 'Pause':
        return [1000*1000, 'Run']
    else:
        return [1*1000, 'Pause']

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
@app.callback([Output('row_graph_ch1', 'style'),
               Output('row_graph_ch2', 'style'),
               Output('row_graph_ch3', 'style'),
               Output('row_graph_ch4', 'style'),
               Output('row_graph_ch5', 'style'),
               Output('row_graph_ch6', 'style')],
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

    with open('temp/tree.txt', 'r') as file:
        checked_global = [current_place.rstrip() for current_place in file.readlines()]

    checked_diff = list(set(checked).difference(checked_global))

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

    with open('temp/tree.txt', 'w') as file:
        file.writelines('%s\n' % item for item in checked_global)

    if checked_global:
        if checked_global[0].find('CH') > -1:
            return checked_global, DIV_body_right_channels

        if checked_global[0].find('dev') > -1:
            return checked_global, DIV_body_right_devices

        if checked_global[0].find('loc') > -1:
            return checked_global, DIV_body_right_locations

    return checked_global, DIV_body_right_none  # Once implemented, rather return DIV_body_right_none



#Devices=========================================================================================================================#
# Update placeholders in the inputs
@app.callback([Output('h4_device_id', 'children'),
               Output('in_alias_ch1', 'placeholder'),
               Output('in_sf_1', 'placeholder'),
               Output('in_alias_ch2', 'placeholder'),
               Output('in_sf_2', 'placeholder'),
               Output('in_alias_ch3', 'placeholder'),
               Output('in_sf_3', 'placeholder'),
               Output('in_alias_ch4', 'placeholder'),
               Output('in_sf_4', 'placeholder'),
               Output('in_alias_ch5', 'placeholder'),
               Output('in_sf_5', 'placeholder'),
               Output('in_alias_ch6', 'placeholder'),
               Output('in_sf_6', 'placeholder'),
               Output('in_alias_dev', 'value')],
              [Input('nav_tree', 'checked')])
def placeholders_update(deviceid):

    placeholder_list = []

    deviceid = utils.get_devid()

    placeholder_list.append(deviceid + ':')

    if deviceid:
        channels_ld = utils.get_channels()
        devices_ld = utils.get_devices()


        for dict in channels_ld:
            placeholder_list.append(dict['alias'])
            placeholder_list.append(dict['scaling_fact'])

        for dict in devices_ld:
            if dict['name'] == deviceid:
                placeholder_list.append(dict['alias'])

    else:
        placeholder_list = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']

    return placeholder_list

# Set channel aliases, channel scaling factors, device aliases and update the nav_tree nodes
@app.callback([Output('in_alias_ch1', 'disabled'),
               Output('in_sf_1', 'disabled'),
               Output('btn_ch1', 'children'),
               Output('in_alias_ch2', 'disabled'),
               Output('in_sf_2', 'disabled'),
               Output('btn_ch2', 'children'),
               Output('in_alias_ch3', 'disabled'),
               Output('in_sf_3', 'disabled'),
               Output('btn_ch3', 'children'),
               Output('in_alias_ch4', 'disabled'),
               Output('in_sf_4', 'disabled'),
               Output('btn_ch4', 'children'),
               Output('in_alias_ch5', 'disabled'),
               Output('in_sf_5', 'disabled'),
               Output('btn_ch5', 'children'),
               Output('in_alias_ch6', 'disabled'),
               Output('in_sf_6', 'disabled'),
               Output('btn_ch6', 'children'),
               Output('nav_tree', 'nodes')],
              [Input('in_alias_dev', 'value'),
               Input('btn_ch1', 'n_clicks'),
               Input('btn_ch2', 'n_clicks'),
               Input('btn_ch3', 'n_clicks'),
               Input('btn_ch4', 'n_clicks'),
               Input('btn_ch5', 'n_clicks'),
               Input('btn_ch6', 'n_clicks'),
               Input('btn_ch1', 'children'),
               Input('btn_ch2', 'children'),
               Input('btn_ch3', 'children'),
               Input('btn_ch4', 'children'),
               Input('btn_ch5', 'children'),
               Input('btn_ch6', 'children'),
               Input('in_alias_ch1', 'value'),
               Input('in_alias_ch2', 'value'),
               Input('in_alias_ch3', 'value'),
               Input('in_alias_ch4', 'value'),
               Input('in_alias_ch5', 'value'),
               Input('in_alias_ch6', 'value'),
               Input('in_sf_1', 'value'),
               Input('in_sf_2', 'value'),
               Input('in_sf_3', 'value'),
               Input('in_sf_4', 'value'),
               Input('in_sf_5', 'value'),
               Input('in_sf_6', 'value'),
               Input('in_alias_ch1', 'disabled'),
               Input('in_alias_ch2', 'disabled'),
               Input('in_alias_ch3', 'disabled'),
               Input('in_alias_ch4', 'disabled'),
               Input('in_alias_ch5', 'disabled'),
               Input('in_alias_ch6', 'disabled'),
               Input('in_sf_1', 'disabled'),
               Input('in_sf_2', 'disabled'),
               Input('in_sf_3', 'disabled'),
               Input('in_sf_4', 'disabled'),
               Input('in_sf_5', 'disabled'),
               Input('in_sf_6', 'disabled')])
def update_dev_ch_tree(dev_alias,
                       n1, n2, n3, n4, n5, n6,
                       b1, b2, b3, b4, b5, b6,
                       a1, a2, a3, a4, a5, a6,
                       s1, s2, s3, s4, s5, s6,
                       ad1, ad2, ad3, ad4, ad5, ad6,
                       sd1, sd2, sd3, sd4, sd5, sd6):

    out = []

    # if utils.get_devid() is None:
    #     print('raised')
    #     raise PreventUpdate
    # print('not raised')

    # if checked:
    #     print(checked)

    with open('temp/tree.txt', 'r') as file:
        checked_global = [current_place.rstrip() for current_place in file.readlines()]
        deviceid = (checked_global[0].split('dev'))[-1]
        file.close()

    devices_ld = utils.get_devices()
    if dev_alias:
        for i in range(len(devices_ld)):
            if devices_ld[i]['name'] == deviceid:
                devices_ld[i]['alias'] = dev_alias
    utils.update_devices(devices_ld)

    channels_ld = utils.get_channels()
    # print('\nchannels_ld1')
    # print(channels_ld)

    # channels_ld[0]['name'] = 'CH1'
    # channels_ld[1]['name'] = 'CH2'
    # channels_ld[2]['name'] = 'CH3'
    # channels_ld[3]['name'] = 'CH4'
    # channels_ld[4]['name'] = 'CH5'
    # channels_ld[5]['name'] = 'CH6'

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

    clicked_btns = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn_ch1' in clicked_btns:
        if channels_ld[0]['disabled'] == 'Enabled':
            channels_ld[0]['disabled'] = 'Disabled'
        else:
            channels_ld[0]['disabled'] = 'Enabled'
    if 'btn_ch2' in clicked_btns:
        if channels_ld[1]['disabled'] == 'Enabled':
            channels_ld[1]['disabled'] = 'Disabled'
        else:
            channels_ld[1]['disabled'] = 'Enabled'
    if 'btn_ch3' in clicked_btns:
        if channels_ld[2]['disabled'] == 'Enabled':
            channels_ld[2]['disabled'] = 'Disabled'
        else:
            channels_ld[2]['disabled'] = 'Enabled'
    if 'btn_ch4' in clicked_btns:
        if channels_ld[3]['disabled'] == 'Enabled':
            channels_ld[3]['disabled'] = 'Disabled'
        else:
            channels_ld[3]['disabled'] = 'Enabled'
    if 'btn_ch5' in clicked_btns:
        if channels_ld[4]['disabled'] == 'Enabled':
            channels_ld[4]['disabled'] = 'Disabled'
        else:
            channels_ld[4]['disabled'] = 'Enabled'
    if 'btn_ch6' in clicked_btns:
        if channels_ld[5]['disabled'] == 'Enabled':
            channels_ld[5]['disabled'] = 'Disabled'
        else:
            channels_ld[5]['disabled'] = 'Enabled'

    if channels_ld[0]['disabled'] == 'Disabled':
        out.append(True)
        out.append(True)
        out.append('Disabled')
    else:
        out.append(False)
        out.append(False)
        out.append('Enabled')
    if channels_ld[1]['disabled'] == 'Disabled':
        out.append(True)
        out.append(True)
        out.append('Disabled')
    else:
        out.append(False)
        out.append(False)
        out.append('Enabled')
    if channels_ld[2]['disabled'] == 'Disabled':
        out.append(True)
        out.append(True)
        out.append('Disabled')
    else:
        out.append(False)
        out.append(False)
        out.append('Enabled')
    if channels_ld[3]['disabled'] == 'Disabled':
        out.append(True)
        out.append(True)
        out.append('Disabled')
    else:
        out.append(False)
        out.append(False)
        out.append('Enabled')
    if channels_ld[4]['disabled'] == 'Disabled':
        out.append(True)
        out.append(True)
        out.append('Disabled')
    else:
        out.append(False)
        out.append(False)
        out.append('Enabled')
    if channels_ld[5]['disabled'] == 'Disabled':
        out.append(True)
        out.append(True)
        out.append('Disabled')
    else:
        out.append(False)
        out.append(False)
        out.append('Enabled')

    # print('\nchannels_ld2')
    # print(channels_ld)

    # utils.update_channels('config/' + deviceid + '.csv', channels_ld)
    utils.update_channels('config/channels.csv', channels_ld)

    tree_nodes = utils.update_tree_nodes(utils.get_locations(), utils.get_devices(), utils.get_channels())
    out.append(tree_nodes)

    return out



#Main============================================================================================================================#
if __name__ == '__main__':
    # app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)
    app.run_server(debug=True)
