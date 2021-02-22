# Go through all comments in all files and cleanup/reimplement commented code

import numpy as np
import pandas as pd
from shutil import copyfile

import plotly.graph_objects as go

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_useful_components as duc

import utils
from app import app

#----------------------------------------------------------------------------------------------------------------------#
colorlist = ['#FF4F00', '#FFF400', '#FF0056', "#5E0DAC", '#60AAED', '#1CA776']

#----------------------------------------------------------------------------------------------------------------------#
df = utils.get_df('../data/sensor_data.csv')
locations_ld = utils.get_locations()
devices_ld = utils.get_devices()
channels_ld = utils.get_channels()
checkboxtree_nodes = utils.checkboxtree_nodes(locations_ld, devices_ld, channels_ld)

# print('\nlocations_ld')
# print(locations_ld)
# print('\ndevices_ld')
# print(devices_ld)
# print('\nchannels_ld')
# print(channels_ld)

#----------------------------------------------------------------------------------------------------------------------#
body_left_card_tree = dbc.CardBody(
    [
        # html.Div(duc.CheckBoxTree(id="cb_input", nodes=checkboxtree_nodes, showNodeIcon=False))
        dbc.Row(html.Div(duc.CheckBoxTree(id="cb_input", nodes=checkboxtree_nodes, showNodeIcon=False)), className='mb-4'),
        dbc.Row(
            html.Div([
                dcc.Checklist(
                    id='options',
                    options=[
                        {'label': 'Tree can be Disabled', 'value': 'disabled'},
                        {'label': 'Expand Disabled', 'value': 'expandDisabled'},
                        {'label': 'Expand when clicked', 'value': 'expandOnClick'},
                        {'label': 'Do not cascade', 'value': 'noCascade'},
                        {'label': 'Only Leaf Checkboxes', 'value': 'onlyLeafCheckboxes'},
                        {'label': 'Optimistic Toggle', 'value': 'optimisticToggle'},
                        {'label': 'Show Nodes Icons', 'value': 'showNodeIcon'},
                    ],
                    value=['optimisticToggle', 'showNodeIcon'],
                )
            ])
        ),
        dbc.Row(html.Div(id='checked-output'), className='mb-4'),
        dbc.Row(html.Div(id='expanded-output'), className='mb-4'),
        # dbc.Button("22229D7", id="btn_d1", className="mb-0", color="secondary", style={'width': '100%'}, size='lg'),
        # dbc.Collapse(
        #     children=[
        #         # dbc.Row([
        #         #     dbc.Col([html.H5("↳")], width=1),
        #         #     dbc.Col([dbc.Button("d1_ch1", id="btn_d1_ch1", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm')])
        #         # ]),
        #         dbc.Button("d1_ch1", id="btn_d1_ch1", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d1_ch2", id="btn_d1_ch2", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d1_ch3", id="btn_d1_ch3", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d1_ch4", id="btn_d1_ch4", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d1_ch5", id="btn_d1_ch5", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d1_ch6", id="btn_d1_ch6", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #     ],
        #     id="clp_d1",
        # ),
        # dbc.Button("22229D9", id="btn_d2", className="mb-0", color="secondary", style={'width': '100%'}, size='lg'),
        # dbc.Collapse(
        #     children=[
        #         dbc.Button("d2_ch1", id="btn_d2_ch1", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d2_ch2", id="btn_d2_ch2", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d2_ch3", id="btn_d2_ch3", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d2_ch4", id="btn_d2_ch4", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d2_ch5", id="btn_d2_ch5", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #         dbc.Button("d2_ch6", id="btn_d2_ch6", className="mb-0", color="warning", style={'width': '100%', 'height': '30px'}, size='sm'),
        #     ],
        #     id="clp_d2",
        # ),
    ]
),

body_right_card_caption = dbc.CardBody(
    [
        html.H3(id='body_right_card_caption', children='Sigfox Sensor Network Real-time Monitoring', className="text-left bg-primary"),
        # dbc.Row(html.H3(id='body_right_card_caption', children='Sigfox Sensor Network Real-time Monitoring', className="text-left bg-secondary")),
        # dbc.Row(html.H6(id='h6_channel_string_statistics', children=utils.string_channels()))
    ]
)

body_right_card_dropdown = dbc.CardBody(
    dbc.Row(  # Row for dropdowns
        [
            dbc.Col(html.P('''Sensor ID:''', style={'margin-right': '10px', 'margin-top': '5px', 'textAlign': 'left'}), width=1),
            dbc.Col(
                dcc.Dropdown(id='dd_id',
                             options=utils.get_options(df['deviceId'].unique(), devices_ld),
                             multi=True,
                             style={'color': 'black', 'background-color': 'white'}
                ),
                width=3,
            ),
            dbc.Col(html.P('''Channel:''', style={'margin-right': '10px', 'margin-top': '5px', 'textAlign': 'left'}), width=1),
            dbc.Col(
                dcc.Dropdown(id='dd_channel',
                             options=utils.get_options(df['data'].unique(), channels_ld),
                             style={'color': 'black', 'background-color': 'white'}
                ),
                width=3,
            ),
        ],
        # no_gutters = True,
    ),
)

body_right_metrics_left_graph_timeseries = dcc.Graph(id='graph_timeseries', animate=True)

body_right_metrics_left_graph_change = dcc.Graph(id='graph_change', animate=True)

body_right_metrics_right_object = [
    dbc.CardHeader(children=["Device <devid>"]),
    dbc.CardBody(
        [
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon('Name', addon_type="prepend"),
                    dbc.Input(placeholder=""),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon('@', addon_type="prepend"),
                    dbc.Input(placeholder=""),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon('@', addon_type="prepend"),
                    dbc.Input(placeholder=""),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon('@', addon_type="prepend"),
                    dbc.Input(placeholder=""),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon('@', addon_type="prepend"),
                    dbc.Input(placeholder=""),
                ],
                className="mb-3",
            ),
        ]
    )
]

DIV_body_right = html.Div(  # Div for body_right
    [
        dbc.Row([  # Row body_right_card_caption
            dbc.Col
            (
                dbc.Card(body_right_card_caption, color="primary"),
                className="mb-2"
            )
        ]),
        dbc.Row([  # Row body_right_card_dropdown
            dbc.Col
            (
                dbc.Card(body_right_card_dropdown, color="primary"),
                className="mb-2"
            )
        ]),
        dbc.Row([  # Row body_right_metrics
            dbc.Col(  # Col body_right_metrics_left
                [
                    dbc.Row([  # Row for body_right_metrics_left_graph_timeseries
                        dbc.Col
                        (
                            dbc.Card(body_right_metrics_left_graph_timeseries, color="primary"),
                            className = "mb-2",
                        )
                    ]),
                    dbc.Row([  # Row for body_right_metrics_left_graph_change
                        dbc.Col
                        (
                            dbc.Card(body_right_metrics_left_graph_change, color="primary"),
                            className = "mb-2",
                        )
                    ]),
                ],
                width = 8,
            ),
            dbc.Col(  # Col body_right_metrics_right
                [
                    dbc.Row([  # Row for body_right_metrics_right_object
                        dbc.Col
                        (
                            dbc.Card(body_right_metrics_right_object, color="primary"),
                            className = "mb-2",
                        )
                    ]),
                ],
                width = 4,
            )
        ]),

    ],
),

#--------------------------------------------------------------------------------------------------------------------------------#
layout = html.Div([
    dbc.Container(
        [
            dbc.Row(  # Row for body
                [
                    dcc.Interval(id='graph_update', interval= 1*1000, n_intervals=0),
                    dbc.Col(  # Col for body_left
                        [
                            dbc.Card(body_left_card_tree, color="primary", style={'height': '100%'})
                        ],
                        width = 2
                    ),
                    dbc.Col(  # Col for body_right
                        id = 'col_body_right',
                        children = [],
                        width = 10,
                    )
                ],
            )
        ],
        fluid=True
    )
])

#Tree Navigation-----------------------------------------------------------------------------------------------------------------#
@app.callback(Output('col_body_right', 'children'),
              [Input('col_body_right', 'children')])
def DIV_body_right_update(x):
    return DIV_body_right

@app.callback(
    [Output('checked-output', 'children'),
     Output('expanded-output', 'children')],
    [Input('cb_input', 'checked'),
     Input('cb_input', 'expanded')])
def display_output(checked, expanded):
    if checked and len(checked) > 0:
        res1 = 'You have checked {}'.format(' '.join(checked))
    else:
        res1 = 'No node is checked'

    if expanded and len(expanded) > 0:
        res2 = 'You have expanded {}'.format(' '.join(expanded))
    else:
        res2 = 'No node is expanded'

    return [res1, res2]

@app.callback(
    [Output('cb_input', 'disabled'),
     Output('cb_input', 'expandDisabled'),
     Output('cb_input', 'expandOnClick'),
     Output('cb_input', 'noCascade'),
     Output('cb_input', 'onlyLeafCheckboxes'),
     Output('cb_input', 'optimisticToggle'),
     Output('cb_input', 'showNodeIcon')],
    [Input('options', 'value')]
)
def configure_display(value):
    list_options = ['disabled',
                    'expandDisabled',
                    'expandOnClick',
                    'noCascade',
                    'onlyLeafCheckboxes',
                    'optimisticToggle',
                    'showNodeIcon']
    if value:
        return [list_option in value for list_option in list_options]
    else:
        raise PreventUpdate

#Data Processing-----------------------------------------------------------------------------------------------------------------#
# Apply scaling factors
@app.callback(Output('body_right_card_caption', 'children'),
              Input('graph_update', 'n_intervals'))
def channel_string_scaling_factor_update(x):

    df = pd.read_csv('../data/sensor_data.csv')
    channels_ld = utils.get_channels()

    scaling_fact = 1.0
    df_scaled = df
    df_scaled['value'] = df_scaled['value'].astype(float)
    df_scaled['change'] = df_scaled['change'].astype(float)

    for dict in channels_ld:
        channel = dict['name']
        scaling_fact = float(dict['scaling_fact'])
        df_scaled.loc[df_scaled['data']==channel, 'value'] = df_scaled[df_scaled['data']==channel]['value'] * scaling_fact
        df_scaled.loc[df_scaled['data']==channel, 'change'] = df_scaled[df_scaled['data']==channel]['change'] * scaling_fact
    df_scaled.to_csv('../data/sensor_data_temp.csv', index=False, header=True)
    copyfile('../data/sensor_data_temp.csv', '../data/sensor_data_scaled.csv')  # TURN THIS ON AGAIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    return 'Sigfox Sensor Network Real-time Monitoring'

#Graphing------------------------------------------------------------------------------------------------------------------------#
# Update graph_timeseries based on the dropdown
@app.callback(Output('graph_timeseries', 'figure'),
              [Input('dd_id', 'value'),
               Input('dd_channel', 'value'),
               Input('graph_update', 'n_intervals')])
def update_graph_timeseries(ids, data, n):

    df = pd.read_csv('../data/sensor_data_scaled.csv', parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])  # remove this, make the graph read directly from the timestamp column if possible

    trace = []

    if ids and data:
        df_data = df[df['data'] == data]
        xmin = df_data.index.min()
        xmax = df_data.index.max()
        ymin = df_data['value'].min() - 0.05 * np.abs(df_data['value'].max())
        ymax = df_data['value'].max() + 0.05 * np.abs(df_data['value'].max())
        for id in ids:
            df_data_id = df_data[df_data['deviceId'] == id]
            trace.append(go.Scatter(x=df_data_id.index,
                                    y=df_data_id['value'],
                                    mode='lines+markers',
                                    opacity=0.7,
                                    line={'width': 3},
                                    name=id,
                                    textposition='bottom center'))
    else:
        df_clear = df
        df_clear['value'].values[:] = 0
        xmin = df.index.min()
        xmax = df.index.max()
        ymin = -100
        ymax = 100
        trace.append(go.Scatter(x=df_clear.index,
                                y=df_clear['value'],
                                mode='lines',
                                opacity=0.7,
                                line={'width': 3},
                                textposition='bottom center'
                    )
        )

    traces = [trace]
    data = [val for sublist in traces for val in sublist]

    figure = {'data': data,
              'layout': go.Layout(
                  colorway=colorlist,
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  hovermode='x',
                  height=500,
                  autosize=True,
                  title={'text': 'Sensor Data', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [xmin, xmax], 'gridcolor': 'white', 'gridwidth': 0.5},
                  yaxis={'range': [ymin, ymax], 'gridcolor': 'white'},
              ),
    }

    return figure

# Update graph_change based on the dropdown
@app.callback(Output('graph_change', 'figure'),
              [Input('dd_id', 'value'),
               Input('dd_channel', 'value'),
               Input('graph_update', 'n_intervals')])
def update_graph_change(ids, data, n):

    df = pd.read_csv('../data/sensor_data_scaled.csv', parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])  # remove this, make the graph read directly from the timestamp column if possible

    trace = []

    if ids and data:
        df_data = df[df['data'] == data]
        xmin = df_data.index.min()
        xmax = df_data.index.max()
        ymin = df_data['change'].min() - 0.05 * np.abs(df_data['change'].max())
        ymax = df_data['change'].max() + 0.05 * np.abs(df_data['change'].max())
        for id in ids:
            df_data_id = df_data[df_data['deviceId'] == id]
            trace.append(go.Scatter(x=df_data_id.index,
                                    y=df_data_id['change'],
                                    mode='lines+markers',
                                    line={'width': 3},
                                    opacity=0.7,
                                    name=id,
                                    textposition='bottom center'
                        )
            )
    else:
        df_clear = df
        df_clear['change'].values[:] = 0
        xmin = df.index.min()
        xmax = df.index.max()
        ymin = -10
        ymax = 10
        trace.append(go.Scatter(x=df_clear.index,
                                y=df_clear['change'],
                                mode='lines',
                                line={'width': 3},
                                opacity=0.7,
                                textposition='bottom center'
                    )
        )

    traces = [trace]
    data = [val for sublist in traces for val in sublist]

    figure = {'data': data,
              'layout': go.Layout(
                  colorway=colorlist,
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  height=350,
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Change', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [xmin, xmax], 'gridcolor': 'white', 'gridwidth': 0.5},
                  yaxis={'range': [ymin, ymax], 'gridcolor': 'white'},
              ),
    }

    return figure

#Accordeon-----------------------------------------------------------------------------------------------------------------------#
# # Callback function to for btn_d1
# @app.callback(Output("clp_d1", "is_open"),
#               [Input("btn_d1", "n_clicks")],
#               [State("clp_d1", "is_open")])
# def toggle_collapse_d1(n, is_open):
#     if n:
#         return not is_open
#     return is_open
#
# # Callback function to for btn_d1_ch1
# @app.callback(Output("btn_d1_ch1", "color"),
#               [Input("btn_d1_ch1", "n_clicks"),
#                Input("btn_d1_ch1", "color")])
# def toggle_collapse_d1_ch1(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d1_ch2
# @app.callback(Output("btn_d1_ch2", "color"),
#               [Input("btn_d1_ch2", "n_clicks"),
#                Input("btn_d1_ch2", "color")])
# def toggle_collapse_d1_ch2(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d1_ch3
# @app.callback(Output("btn_d1_ch3", "color"),
#               [Input("btn_d1_ch3", "n_clicks"),
#                Input("btn_d1_ch3", "color")])
# def toggle_collapse_d1_ch3(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d1_ch4
# @app.callback(Output("btn_d1_ch4", "color"),
#               [Input("btn_d1_ch4", "n_clicks"),
#                Input("btn_d1_ch4", "color")])
# def toggle_collapse_d1_ch4(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d1_ch5
# @app.callback(Output("btn_d1_ch5", "color"),
#               [Input("btn_d1_ch5", "n_clicks"),
#                Input("btn_d1_ch5", "color")])
# def toggle_collapse_d1_ch5(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d1_ch6
# @app.callback(Output("btn_d1_ch6", "color"),
#               [Input("btn_d1_ch6", "n_clicks"),
#                Input("btn_d1_ch6", "color")])
# def toggle_collapse_d1_ch6(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d2
# @app.callback(Output("clp_d2", "is_open"),
#               [Input("btn_d2", "n_clicks")],
#               [State("clp_d2", "is_open")])
# def toggle_collapse_1_2(n, is_open):
#     if n:
#         return not is_open
#     return is_open
#
# # Callback function to for btn_d2_ch1
# @app.callback(Output("btn_d2_ch1", "color"),
#               [Input("btn_d2_ch1", "n_clicks"),
#                Input("btn_d2_ch1", "color")])
# def toggle_collapse_d2_ch1(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d2_ch2
# @app.callback(Output("btn_d2_ch2", "color"),
#               [Input("btn_d2_ch2", "n_clicks"),
#                Input("btn_d2_ch2", "color")])
# def toggle_collapse_d2_ch2(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d2_ch3
# @app.callback(Output("btn_d2_ch3", "color"),
#               [Input("btn_d2_ch3", "n_clicks"),
#                Input("btn_d2_ch3", "color")])
# def toggle_collapse_d2_ch3(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d2_ch4
# @app.callback(Output("btn_d2_ch4", "color"),
#               [Input("btn_d2_ch4", "n_clicks"),
#                Input("btn_d2_ch4", "color")])
# def toggle_collapse_d2_ch4(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d2_ch5
# @app.callback(Output("btn_d2_ch5", "color"),
#               [Input("btn_d2_ch5", "n_clicks"),
#                Input("btn_d2_ch5", "color")])
# def toggle_collapse_d2_ch5(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
#
# # Callback function to for btn_d2_ch6
# @app.callback(Output("btn_d2_ch6", "color"),
#               [Input("btn_d2_ch6", "n_clicks"),
#                Input("btn_d2_ch6", "color")])
# def toggle_collapse_d2_ch6(n, color):
#     if color=='warning':
#         return 'secondary'
#     return 'warning'
