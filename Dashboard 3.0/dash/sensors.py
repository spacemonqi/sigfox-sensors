import numpy as np
import pandas as pd
from shutil import copyfile

import plotly.graph_objects as go

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import utils
from app import app

#----------------------------------------------------------------------------------------------------------------------#
df = utils.get_df('../data/sensor_data.csv')
channel_ld = utils.get_channels()
device_ld = utils.get_devices()

colorlistlist_sensor = [['#63D1F4'], ['#E0FFFF'], ['#95C8D8'], ["#008ECC"], ['#6593D5'], ['#73C2FB']]
colorlist_meas = ['#FFF400', '#FF4F00', '#FF0056', "#5E0DAC", '#60AAED', '#1CA776']

#----------------------------------------------------------------------------------------------------------------------#
layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Selected Channels: "))]),
        dbc.Row([dbc.Col(html.H6(id='h6_channel_string_sensors', children=utils.string_channels()), className="mb-4")]),

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
                                         style={'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
                dbc.Col(children=[
                            html.P('''Sensor ID:'''),
                            dcc.Dropdown(id='dd_id_meas',
                                         options=utils.get_options(df['deviceId'].unique(), device_ld),
                                         multi=True,
                                         style={'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
                dbc.Col(children=[
                            html.P('''Measurement:'''),
                            dcc.Dropdown(id='dd_measurement_meas',
                                         options=utils.get_options(df['data'].unique(), channel_ld),
                                         style={'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                )
            ]),
        dcc.Graph(id='meas_timeseries', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),
        dcc.Graph(id='meas_change', config={'displayModeBar': False}, animate=True, style={'margin-bottom': '10px'}),

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
                                         style={'margin-bottom': '10px',
                                                'color': 'black',
                                                'background-color': 'white'}
                            ),
                        ],
                        width = 4,
                ),
                dbc.Col(children=[
                            html.P('''Sensor ID:'''),
                            dcc.Dropdown(id='dd_id_sensor',
                                         options=utils.get_options(df['deviceId'].unique(), device_ld),
                                         style={'margin-bottom': '10px',
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

        # dbc.Row([dbc.Col(dbc.Card(html.H3(children='Cumulative Data by Sensor Type', className="text-center bg-primary"),
        #                           body=True,
        #                           color="primary"),
        #          className="mb-4 mt-5")]),
        # dbc.Row([
        #         dbc.Col(children=[
        #                     html.P('''Sensor type:'''),
        #                     dcc.Dropdown(id='dd_type_type',
        #                                  options=[{'label': 'STM32WL55', 'value': 'STM32WL55'},
        #                                           {'label': 'S2LP', 'value': 'S2LP'},
        #                                           {'label': 'TI', 'value': 'TI'}],
        #                                  style={'margin-bottom': '10px',
        #                                         'color': 'black',
        #                                         'background-color': 'white'}
        #                     ),
        #                 ],
        #                 width = 4,
        #         ),
        # ]),

        dcc.Interval(id='graph_update', interval= 1 * 1000, n_intervals=0),
    ])
])

#----------------------------------------------------------------------------------------   ------------------------------#
# Callback function to update the channel string and to apply all the scaling factors
@app.callback(Output('h6_channel_string_sensors', 'children'),
              Input('graph_update', 'n_intervals'))
def channel_string_scaling_factor_update(x):

    df = pd.read_csv('../data/sensor_data.csv')
    channels_ld = utils.get_channels()

    scaling_fact = 1.0
    df_scaled = df
    df_scaled['value'] = df_scaled['value'].astype(float)
    df_scaled['change'] = df_scaled['change'].astype(float)

    for dict in channels_ld:
        channel = dict['channel']
        scaling_fact = float(dict['scaling_fact'])
        df_scaled.loc[df_scaled['data']==channel, 'value'] = df_scaled[df_scaled['data']==channel]['value'] *scaling_fact
        df_scaled.loc[df_scaled['data']==channel, 'change'] = df_scaled[df_scaled['data']==channel]['change'] * scaling_fact
    df_scaled.to_csv('../data/sensor_data_temp.csv', index=False, header=True)
    copyfile('../data/sensor_data_temp.csv', '../data/sensor_data_scaled.csv')

    return utils.string_channels()

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
    style = {'margin-bottom': '10px', 'color': 'black', 'background-color': '#848a8e'}
    channel_ld = utils.get_channels()
    device_ld = utils.get_devices()
    disabled = True
    options_id = []
    options_data = []
    if value:
        disabled = False
        style = {'margin-bottom': '10px', 'color': 'black', 'background-color': 'white'}
    if value == 'STM32WL55':
        options_id = utils.get_options(df['deviceId'].unique(), device_ld)
        options_data = utils.get_options(df['data'].unique(), channel_ld)

    return [disabled, "", style, options_id, disabled, "", style, options_data]

# Callback function to update the meas_timeseries based on the dropdown
@app.callback(Output('meas_timeseries', 'figure'),
              [Input('dd_id_meas', 'value'),
               Input('dd_measurement_meas', 'value'),
               Input('graph_update', 'n_intervals')])
def update_meas_timeseries(ids, data, n):

    # file = open('sensor_data_scaled.csv')
    # if file.closed:
    #   print 'file is closed'

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
    device_ld = utils.get_devices()
    style = {'margin-bottom': '10px', 'color': 'black', 'background-color': '#848a8e'}
    disabled = True
    options_id = []
    if value:
        disabled = False
        style = {'margin-bottom': '10px', 'color': 'black', 'background-color': 'white'}
    if value == 'STM32WL55':
        options_id = utils.get_options(df['deviceId'].unique(), device_ld)

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

    df = pd.read_csv('../data/sensor_data_scaled.csv', parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])  # remove this, make the graph read directly from the timestamp column if possible

    channels_ld = utils.get_channels()
    figures = []
    data = df['data'].unique()

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
