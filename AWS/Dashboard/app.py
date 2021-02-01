#!/usr/local/bin/python3

import pdb

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

def get_options(list_data):
    dict_list = []
    for i in list_data:
        dict_list.append({'label':i, 'value':i})

    return dict_list

# Load data
df = pd.read_csv('data/sensor_data.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['timestamp'])

# Initialize the app
app = dash.Dash(__name__);

# Define the app
app.layout = html.Div(children=[
                          html.Div(className='row',
                                   children=[
                                      html.Div(className='four columns div-user-controls',
                                               children = [
                                                    html.H2('Sigfox Demo'),
                                                    html.P('''Visualising sensor data from the STM32WL55'''),
                                                    html.P('''Select reading below.'''),
                                                    html.Div(className='div-for-dropdown',
                                                             children=[
                                                                dcc.Dropdown(id='dataselector',
                                                                options=get_options(df['data'].unique()),
                                                                placeholder='temperature',
                                                                clearable=False,
                                                                value=[df['data'].sort_values()[0]],
                                                                style={'backgroundColor': '#1E1E1E'},
                                                                className='dataselector'
                                                                )
                                                             ],
                                                             style={'color': '#1E1E1E'}
                                                    )
                                               ]
                                      ),
                                      html.Div(className='eight columns div-for-charts bg-grey',
                                               children = [
                                                    dcc.Graph(id='timeseries',
                                                              config={'displayModeBar': False},
                                                              animate=True),
                                                    dcc.Graph(id='change',
                                                              config={'displayModeBar': False},
                                                              animate=True),
                                                    dcc.Interval(
                                                        id='graph-update',
                                                        interval=1*1000, # in milliseconds
                                                        n_intervals=0
                                                    )
                                               ]
                                      )
                                   ]
                          )
                      ]
             )

# Callback function to update the timeseries based on the dropdown
@app.callback(Output('timeseries', 'figure'), [Input('dataselector', 'value'), Input('graph-update', 'n_intervals')])
def update_timeseries(data, n):
    ''' Draw traces of the feature 'value' based on the currently selected data'''

    if not ((data=='humidity') or (data=='pressure') or (data=='temperature')):
        data = 'temperature'

    df = pd.read_csv('data/sensor_data.csv', index_col=0, parse_dates=True)
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

    if data=='pressure':
        figure.update_layout(colorway=['#375CB1'])

    return figure

# Callback function to update the change based on the dropdown
@app.callback(Output('change', 'figure'), [Input('dataselector', 'value'), Input('graph-update', 'n_intervals')])
def update_change(data, n):
    ''' Draw traces of the feature 'change' based one the currently selected data '''

    if not ((data=='humidity') or (data=='pressure') or (data=='temperature')):
        data = 'temperature'

    df = pd.read_csv('data/sensor_data.csv', index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])

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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
