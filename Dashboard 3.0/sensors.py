from app import app
import channels

import numpy as np
import pandas as pd

import plotly.graph_objects as go

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

#----------------------------------------------------------------------------------------------------------------------#
def get_options(list_data):
    dict_list = []
    for i in list_data:
        dict_list.append({'label': i, 'value': i})

    return dict_list

def get_values(list_data):
    dict_list = []
    for i in list_data:
        dict_list.append(i)

    return dict_list

#----------------------------------------------------------------------------------------------------------------------#
df = pd.read_csv('aws/data/sensor_data.csv', parse_dates=True)
df.index = pd.to_datetime(df['timestamp'])

colorlistlist_sensor = [['#FFF400'], ['#FF4F00'], ['#FF0056'], ["#5E0DAC"], ['#60AAED'], ['#1CA776']]
colorlist_meas = ['#FFF400', '#FF4F00', '#FF0056', "#5E0DAC", '#60AAED', '#1CA776']

#----------------------------------------------------------------------------------------------------------------------#
layout = html.Div([
    dbc.Container([
        #--------------------------------------------------------------------------------------------------------------#
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Selected Channels: "))]),
        dbc.Row([dbc.Col(html.H6(id='h6_channel_string_sensors', children=channels.string_channels()), className="mb-4")]),

        #--------------------------------------------------------------------------------------------------------------#
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Data by Measurement', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4")]),
        dbc.Row([
                dbc.Col(children=[
                            html.P('''Sensor type:'''),
                            dcc.Dropdown(id='dd_type_meas',
                                         options=[{'label': 'STM32WL55', 'value': 'STM32WL55'},
                                                  {'label': 'S2LP', 'value': 'S2LP'},
                                                  {'label': 'TI', 'value': 'TI'}],
                                         style={'width': '325px',
                                                'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
                dbc.Col(children=[
                            html.P('''Sensor ID:'''),
                            dcc.Dropdown(id='dd_id_meas',
                                         options=get_options(df['deviceId'].unique()),
                                         multi=True,
                                         style={'width': '325px',
                                                'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
                dbc.Col(children=[
                            html.P('''Measurement:'''),
                            dcc.Dropdown(id='dd_measurement_meas',
                                         options=get_options(df['data'].unique()),
                                         style={'width': '325px',
                                                'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                )
            ]),
        dcc.Graph(id='meas_timeseries', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
        dcc.Graph(id='meas_change', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),

        #--------------------------------------------------------------------------------------------------------------#
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Data by Sensor ID', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4 mt-4")]),
        dbc.Row([
                dbc.Col(children=[
                            html.P('''Sensor type:'''),
                            dcc.Dropdown(id='dd_type_sensor',
                                         options=[{'label': 'STM32WL55', 'value': 'STM32WL55'},
                                                  {'label': 'S2LP', 'value': 'S2LP'},
                                                  {'label': 'TI', 'value': 'TI'}],
                                         style={'width': '325px',
                                                'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
                dbc.Col(children=[
                            html.P('''Sensor ID:'''),
                            dcc.Dropdown(id='dd_id_sensor',
                                         options=get_options(df['deviceId'].unique()),
                                         style={'width': '325px',
                                                'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
            ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='sensor_timeseries_ch1', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
            ]),
            dbc.Col([
                dcc.Graph(id='sensor_timeseries_ch2', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='sensor_timeseries_ch3', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
            ]),
            dbc.Col([
                dcc.Graph(id='sensor_timeseries_ch4', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
            ]),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='sensor_timeseries_ch5', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
            ]),
            dbc.Col([
                dcc.Graph(id='sensor_timeseries_ch6', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
            ]),
        ]),

        #--------------------------------------------------------------------------------------------------------------#
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='Cumulative Data by Sensor Type', className="text-center bg-primary"),
                                  body=True,
                                  color="primary"),
                 className="mb-4 mt-5")]),
        dbc.Row([
                dbc.Col(children=[
                            html.P('''Sensor type:'''),
                            dcc.Dropdown(id='dd_type_type',
                                         options=[{'label': 'STM32WL55', 'value': 'STM32WL55'},
                                                  {'label': 'S2LP', 'value': 'S2LP'},
                                                  {'label': 'TI', 'value': 'TI'}],
                                         style={'width': '325px',
                                                'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
        ]),

        #--------------------------------------------------------------------------------------------------------------#
        dcc.Interval(id='graph_update', interval= 1 * 1000, n_intervals=0),
    ])
])

#----------------------------------------------------------------------------------------------------------------------#
# Callback function to enable/disable & update options of dd_id_meas & dd_measurement_meas based on dd_type_meas
@app.callback([Output('dd_id_meas', 'disabled'),
               Output('dd_id_meas', 'value'),
               Output('dd_id_meas', 'style'),
               Output('dd_id_meas', 'options'),
               Output('dd_measurement_meas', 'disabled'),
               Output('dd_measurement_meas', 'value'),
               Output('dd_measurement_meas', 'style'),
               Output('dd_measurement_meas', 'options')],
              [Input('dd_type_meas', 'value')])
def dd_meas_update(value):
    style = {'width': '330px', 'margin-bottom': '10px', 'color': 'black', 'background-color': '#848a8e'}
    disabled = True
    options_id = []
    options_data = []
    if value:
        disabled = False
        style = {'width': '330px', 'margin-bottom': '10px', 'color': 'black', 'background-color': 'white'}
    if value == 'STM32WL55':
        options_id = get_options(df['deviceId'].unique())
        options_data = get_options(df['data'].unique())

    return [disabled, "", style, options_id, disabled, "", style, options_data]

# Callback function to update the meas_timeseries based on the dropdown
@app.callback(Output('meas_timeseries', 'figure'),
              [Input('dd_id_meas', 'value'),
               Input('dd_measurement_meas', 'value'),
               Input('graph_update', 'n_intervals')])
def update_meas_timeseries(ids, data, n):

    df = pd.read_csv('aws/data/sensor_data.csv', parse_dates=True)
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
                  colorway=colorlist_meas,
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Sensor Data', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [xmin, xmax]},
                  yaxis={'range': [ymin, ymax]},
              ),
    }

    return figure

# Callback function to update the meas_change based on the dropdown
@app.callback(Output('meas_change', 'figure'),
              [Input('dd_id_meas', 'value'),
               Input('dd_measurement_meas', 'value'),
               Input('graph_update', 'n_intervals')])
def update_meas_change(ids, data, n):

    df = pd.read_csv('aws/data/sensor_data.csv', parse_dates=True)
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
                  colorway=colorlist_meas,
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'t': 50},
                  height=250,
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Change', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [xmin, xmax]},
                  yaxis={'range': [ymin, ymax]},
              ),
    }

    return figure

#----------------------------------------------------------------------------------------------------------------------#
# Callback function to enable/disable & update options dd_id_sensor based dd_type_sensor
@app.callback([Output('dd_id_sensor', 'disabled'),
               Output('dd_id_sensor', 'value'),
               Output('dd_id_sensor', 'style'),
               Output('dd_id_sensor', 'options')],
              [Input('dd_type_sensor', 'value')])
def dd_sensor_update(value):
    style = {'width': '330px', 'margin-bottom': '10px', 'color': 'black', 'background-color': '#848a8e'}
    disabled = True
    options_id = []
    if value:
        disabled = False
        style = {'width': '330px', 'margin-bottom': '10px', 'color': 'black', 'background-color': 'white'}
    if value == 'STM32WL55':
        options_id = get_options(df['deviceId'].unique())

    return [disabled, "", style, options_id]

# Callback function to update the sensor_timeseries based on the dropdown
@app.callback([Output('sensor_timeseries_ch1', 'figure'),
               Output('sensor_timeseries_ch2', 'figure'),
               Output('sensor_timeseries_ch3', 'figure'),
               Output('sensor_timeseries_ch4', 'figure'),
               Output('sensor_timeseries_ch5', 'figure'),
               Output('sensor_timeseries_ch6', 'figure')],
              [Input('dd_id_sensor', 'value'),
               Input('graph_update', 'n_intervals')])
def update_sensor_timeseries(id, n):

    df = pd.read_csv('aws/data/sensor_data.csv', parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])  # remove this, make the graph read directly from the timestamp column if possible

    channels_ld = channels.get_channels()
    figures = []
    data = get_values(df['data'].unique())

    i = 0
    for channel in data:

        trace = []

        if id:
            df_data = df[df['data'] == channel]
            df_data_id = df_data[df_data['deviceId'] == id]
            xmin = df_data_id.index.min()
            xmax = df_data_id.index.max()
            ymin = df_data_id['value'].min() - 0.05 * np.abs(df_data_id['value'].max())
            ymax = df_data_id['value'].max() + 0.05 * np.abs(df_data_id['value'].max())
            trace.append(go.Scatter(x=df_data_id.index,
                                    y=df_data_id['value'],
                                    mode='lines+markers',
                                    line={'width': 3},
                                    opacity=0.7,
                                    name=id,
                                    textposition='bottom center'
                        )
            )
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
                                    line={'width': 3},
                                    opacity=0.7,
                                    textposition='bottom center'
                        )
            )

        traces = [trace]
        data = [val for sublist in traces for val in sublist]

        figure = {'data': data,
                  'layout': go.Layout(
                      colorway=colorlistlist_sensor[i],
                      template='plotly_dark',
                      paper_bgcolor='rgba(0, 0, 0, 0)',
                      plot_bgcolor='rgba(0, 0, 0, 0)',
                      margin={'b': 15},
                      hovermode='x',
                      autosize=True,
                      title={'text': channels_ld[i]['alias'], 'font': {'color': 'white'}, 'x': 0.5},
                      xaxis={'range': [xmin, xmax], 'gridcolor': 'white', 'gridwidth': 0.5},
                      yaxis={'range': [ymin, ymax], 'gridcolor': 'white'},
                  ),
                  }

        figures.append(figure)

        i += 1

    return figures
