#!/usr/local/bin/python3

import pdb

import pandas as pd
from datetime import datetime, timedelta

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

# breakpoint()

def get_options(list_data):
    dict_list = []
    for i in list_data:
        dict_list.append({'label':i, 'value':i})

    return dict_list

# Load data
df = pd.read_csv('data/data.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['Date'])

df = pd.read_csv('data/sensor_data.csv')
df.index = datetime.fromtimestamp(df['timestamp'])

# Initialize the app
app = dash.Dash(__name__);

# Define the app
app.layout = html.Div(children=[
                          html.Div(className='row',                                               # Define the row element
                                   children=[
                                      html.Div(className='four columns div-user-controls',        # Define the left element
                                               children = [
                                                    html.H2('Dash - Sigfox Demo'),
                                                    html.P('''Visualising sensor data from the STM32WL55'''),
                                                    html.P('''Select one or more readings from the dropdown below.'''),
                                                    html.Div(className='div-for-dropdown',
                                                             children=[
                                                                dcc.Dropdown(id='dataselector',
                                                                options=get_options(df['data'].unique()),
                                                                multi=True,
                                                                value=[df['data'].sort_values()[0]],
                                                                style={'backgroundColor': '#1E1E1E'},
                                                                className='dataselector')
                                                             ],
                                                             style={'color': '#1E1E1E'}
                                                    )
                                               ]
                                      ),
                                      html.Div(className='eight columns div-for-charts bg-grey',  # Define the right element
                                               children = [
                                                    dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
                                                    dcc.Graph(id='change', config={'displayModeBar': False}), #, animate=True)     CHANGE
                                                    dcc.Interval(
                                                        id='graph-update',
                                                        interval=2*1000, # in milliseconds
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
def update_timeseries(selected_dropdown_value, n):
    ''' Draw traces of the feature 'value' based on the currently selected data'''

    # Load data
    df = pd.read_csv('data/data.csv', index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df['Date'])

    # Initialization
    trace = []
    df_sub = df

    # Draw and append traces for each data type
    for data in selected_dropdown_value:
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
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Sensor Data', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),
              }

    return figure

# # Callback function to update the change based on the dropdown
# @app.callback(Output('change', 'figure'), [Input('dataselector', 'value'), Input('graph-update', 'n_intervals')])
# def update_change(selected_dropdown_value, n):
#     ''' Draw traces of the feature 'change' based one the currently selected data '''
#
#     # Load data
#     df = pd.read_csv('data/data.csv', index_col=0, parse_dates=True)
#     df.index = pd.to_datetime(df['Date'])
#
#     # Initialization
#     trace = []
#     df_sub = df
#
#     # Draw and append traces for each data type
#     for data in selected_dropdown_value:
#         trace.append(go.Scatter(x=df_sub[df_sub['data'] == data].index,
#                                  y=df_sub[df_sub['data'] == data]['change'],
#                                  mode='lines',
#                                  opacity=0.7,
#                                  name=data,
#                                  textposition='bottom center'))
#     traces = [trace]
#     data = [val for sublist in traces for val in sublist]
#
#     # Define Figure
#     figure = {'data': data,
#               'layout': go.Layout(
#                   colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
#                   template='plotly_dark',
#                   paper_bgcolor='rgba(0, 0, 0, 0)',
#                   plot_bgcolor='rgba(0, 0, 0, 0)',
#                   margin={'t': 50},
#                   height=250,
#                   hovermode='x',
#                   autosize=True,
#                   title={'text': 'Daily Change', 'font': {'color': 'white'}, 'x': 0.5},
#                   xaxis={'showticklabels': False, 'range': [df_sub.index.min(), df_sub.index.max()]},
#               ),
#               }
#
#     return figure

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
