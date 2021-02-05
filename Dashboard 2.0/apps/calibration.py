import plotly.graph_objects as go
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from app import app

##################################################
# try to change the direct downlink data in the sigfox backend from here! then a server wont be needed for downlinks
##################################################

# Move this to a function that all pages can access
colorlistlist_sensor = [['#FFF400'], ['#FF4F00'], ['#FF0056'], ["#5E0DAC"], ['#60AAED'], ['#1CA776']]
colorlist_meas = ['#FFF400', '#FF4F00', '#FF0056', "#5E0DAC", '#60AAED', '#1CA776']
channel_name_list = ['Temperature', 'Humidity', 'ADC1', 'ADC2', 'CO2', 'VOC']
channel_name_string = ''
for channel_name in channel_name_list:
    channel_name_string += (channel_name + ", ")
channel_name_string = channel_name_string[0:-2]

layout = html.Div([
    dbc.Container([
        dbc.Row([dbc.Col(html.H1("Sigfox Sensor Network"), className="mb-2")]),
        dbc.Row([dbc.Col(html.H6(children="Selected Channels: "))]),
        dbc.Row([dbc.Col(html.H6(children=channel_name_string), className="mb-4")]),
    ])
])
