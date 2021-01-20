from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import boto3

from datetime import datetime, timedelta
from decimal import Decimal
from pprint import pprint
import json

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import dash

import math
import random
import pandas as pd
import numpy as np

import time
import sys
import os

# Visit http://127.0.0.1:8050/ in your web browser.

#----------------------------------------------------------------------------------------------------------------------#
def scan_items_AWS(dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

            table = dynamodb.Table(tableName)
            response = table.scan()
            return response

def query_and_project_items_AWS(deviceId, last_timestamp, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)

    # Expression attribute names can only reference items in the projection expression.
    response = table.query(
        ProjectionExpression='#id, #ts, payload',
        ExpressionAttributeNames={'#id': 'deviceId', '#ts': 'timestamp'},
        KeyConditionExpression=Key('deviceId').eq(deviceId) & Key('timestamp').between(last_timestamp+1, 2147483647)
    )
    return response['Items']

#----------------------------------------------------------------------------------------------------------------------#
def now():
    return round(datetime.timestamp(datetime.now()))

def scan_to_dataframe():
    columns = ['deviceId', 'timestamp', 'data', 'deviceTypeId', 'seqNumber', 'time']
    index = range(0)
    df = pd.DataFrame(index=index, columns=columns)
    all_items = scan_items_AWS()['Items']
    for i in range(len(all_items)):
        item_dict = {'deviceId': all_items[i]['deviceId'], 'timestamp': datetime.fromtimestamp(int(all_items[i]['timestamp'])),
                    'data': all_items[i]['payload']['data'], 'deviceTypeId': all_items[i]['payload']['deviceTypeId'],
                    'seqNumber': all_items[i]['payload']['seqNumber'], 'time': all_items[i]['payload']['time']}
        df.loc[i] = item_dict
    return df

# Call this:
def last_timestamp(df):
    num_items = len(df.index)
    str = datetime.strftime(df.timestamp[num_items - 1], "%a %b %d %H:%M:%S %Y")
    dt = datetime.strptime(str, "%a %b %d %H:%M:%S %Y")
    timestamp = datetime.timestamp(dt)
    return(round(timestamp))

# Call this:
def append_to_dataframe(df, new_items):

    num_items = len(df.index)

    i = 0
    for new_item in new_items:
        item_dict = {'deviceId': new_item['deviceId'], 'timestamp': datetime.fromtimestamp(int(new_item['timestamp'])),
                    'data': new_item['payload']['data'], 'deviceTypeId': new_item['payload']['deviceTypeId'],
                    'seqNumber': new_item['payload']['seqNumber'], 'time': new_item['payload']['time']}
        df.loc[i+num_items] = item_dict
        i += 1

    return df

#----------------------------------------------------------------------------------------------------------------------#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
demo = dash.Dash(__name__, external_stylesheets=external_stylesheets)

file = open("config.txt", 'r')
tableName = file.readline().rstrip()
online = int(file.readline())

#----------------------------------------------------------------------------------------------------------------------#

demo.layout = html.Div(
    html.Div([
        html.H4('Sigfox Demo Data'),
        dcc.Graph(id='sigfox-demo'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@demo.callback(Output('sigfox-demo', 'figure'), Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    # Scan the table to a DataFrame
    df_sigfox = scan_to_dataframe()

    data = {
        'time': [],
        'payload_data': []
    }

    for i in range(len(df_sigfox.index)):
        time = df_sigfox.timestamp[i]
        payload_data = df_sigfox.data[i]
        data['time'].append(time)
        data['payload_data'].append(payload_data)

    fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)

    fig.append_trace({
        'x': data['time'],
        'y': data['payload_data'],
        'name': 'payload_data',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig

#----------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    demo.run_server(debug=True)
