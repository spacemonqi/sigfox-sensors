from app import app

import numpy as np
import pandas as pd

import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

#----------------------------------------------------------------------------------------------------------------------#

def get_options(list_data):
    dict_list = []
    for i in list_data:
        dict_list.append({'label':i, 'value':i})

    return dict_list

df = pd.read_csv('aws/data/sensor_data.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['timestamp'])

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children='Humidity, temperature, VOC, CO2, ADC'), className="mb-4")]),
        dbc.Row([dbc.Col(dbc.Card(html.H3(children='All Sensors',className="text-center text-light bg-dark"),
                                  body=True,
                                  color="dark"),
                 className="mb-4")]),

        html.P('''Sensor type:'''),
        dcc.Dropdown(id='dd_sensor',
        options=[{'label': 'STM32WL55', 'value': 'STM32WL55'},
                {'label': 'S2LP', 'value': 'S2LP'},
                {'label': 'TI', 'value': 'TI'}],
        clearable=False,
        value=[df['data'].sort_values()[0]],
        style={'width': '300px', 'margin-bottom': '10px'} # 'backgroundColor': '#1E1E1E'
        ),

        html.P('''Sensor ID:'''),
        dcc.Dropdown(id='dd_sensor',
        options=[{'label': 'STM32WL55', 'value': 'STM32WL55'},
                {'label': 'S2LP', 'value': 'S2LP'},
                {'label': 'TI', 'value': 'TI'}],
        clearable=False,
        multi=True,
        value=[df['data'].sort_values()[0]],
        style={'width': '300px', 'margin-bottom': '10px'} # 'backgroundColor': '#1E1E1E'
        ),

        html.P('''Measurement:'''),
        dcc.Dropdown(id='dd_measurement',
        options=get_options(df['data'].unique()),
        clearable=False,
        value=[df['data'].sort_values()[0]],
        style={'width': '300px', 'margin-bottom': '10px'} #, 'margin-bottom': '40px', 'backgroundColor': '#1E1E1E'}
        ),

        # html.P('''Downlinks sent to the STM32WL55'''),
        # html.P('''Select message below'''),
        # html.Div(className='div-for-downlink-dropdown',
        #          style={'color': '#1E1E1E'},
        #          children=[
        #             dcc.Dropdown(id='dldataselector',
        #             className='dldataselector',
        #             options=[
        #                 {'label': 'Time (TAI) calibration ', 'value': 'TAI'},
        #                 {'label': 'Sampling Rate', 'value': 'SR'},
        #                 {'label': 'Downlink Frequency', 'value': 'DF'}
        #             ],
        #             value='NYC',
        #             style={'backgroundColor': '#1E1E1E'}
        #             )
        #          ]
        # ),

        dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
        dcc.Graph(id='change', config={'displayModeBar': False}, animate=True),
        dcc.Interval(id='graph-update', interval=1*1000, n_intervals=0)
    ])
])

# Callback function to update the timeseries based on the dropdown
@app.callback(Output('timeseries', 'figure'), [Input('dd_measurement', 'value'), Input('graph-update', 'n_intervals')])
def update_timeseries(data, n):
    ''' Draw traces of the feature 'value' based on the currently selected data'''

    if not ((data=='Humidity') or (data=='ADC') or (data=='Temperature') or (data=='VOC') or (data=='CO2')):
        data = 'ADC'

    df = pd.read_csv('aws/data/sensor_data.csv', index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])

    trace = []
    df_sub = df
    # df_range = df[df['data']==data] # Uncomment for autoranging
    df_range = df

    trace.append(go.Scatter(x=df_sub[df_sub['data']==data].index,
                            y=df_sub[df_sub['data']==data]['value'],
                            mode='lines',
                            opacity=0.7,
                            name=data,
                            textposition='bottom center'
                 )
    )

    traces = [trace]
    data = [val for sublist in traces for val in sublist]

    figure = {'data': data,
              'layout': go.Layout(
                  colorway=['#FF4F00', '#FFF400', '#FF0056', "#5E0DAC", '#375CB1', '#FF7400'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Sensor Data', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
                  yaxis={'range': [df_range['value'].min()-0.05*np.abs(df_range['value'].max()),
                                   df_range['value'].max()+0.05*np.abs(df_range['value'].max())]},
              ),
    }

    return figure

# Callback function to update the change based on the dropdown
@app.callback(Output('change', 'figure'), [Input('dd_measurement', 'value'), Input('graph-update', 'n_intervals')])
def update_change(data, n):
    ''' Draw traces of the feature 'change' based one the currently selected data '''

    if not ((data=='Humidity') or (data=='ADC') or (data=='Temperature') or (data=='VOC') or (data=='CO2')):
        data = 'ADC'

    df = pd.read_csv('aws/data/sensor_data.csv', index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])

    # change it so that it updates when the file is modified only

    trace = []
    df_sub = df
    # df_range = df[df['data']==data] # Uncomment for autoranging
    df_range = df

    trace.append(go.Scatter(x=df_sub[df_sub['data'] == data].index,
                             y=df_sub[df_sub['data'] == data]['change'],
                             mode='lines',
                             opacity=0.7,
                             name=data,
                             textposition='bottom center'
                )
    )

    traces = [trace]
    data = [val for sublist in traces for val in sublist]

    figure = {'data': data,
              'layout': go.Layout(
                  colorway=['#FF4F00', '#FFF400', '#FF0056', "#5E0DAC", '#375CB1', '#FF7400'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'t': 50},
                  height=250,
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Change', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'showticklabels': False, 'range': [df_sub.index.min(), df_sub.index.max()]},
                  yaxis={'range': [df_range['change'].min()-0.05*np.abs(df_range['change'].max()),
                                   df_range['change'].max()+0.05*np.abs(df_range['change'].max())]},
              ),
    }

    return figure
