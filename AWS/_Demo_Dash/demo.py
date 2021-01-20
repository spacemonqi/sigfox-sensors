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
def create_sigfox_table_AWS(dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[
            {
                'AttributeName': 'deviceId',
                'KeyType': 'HASH' # Partition Key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE' # Sort Key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'deviceId',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        },
        StreamSpecification={
            'StreamEnabled': True,
            'StreamViewType': 'NEW_AND_OLD_IMAGES'
        }
    )
    return table

def delete_sigfox_table_AWS(dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)
    table.delete()

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

def put_item_AWS(deviceId, timestamp, data, deviceTypeId, seqNumber, time, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)
    response = table.put_item(
        Item={
            'deviceId': deviceId,
            'timestamp': timestamp,
            'payload': {
                'data': data,
                'deviceTypeId': deviceTypeId,
                'seqNumber' : seqNumber,
                'time' : time
            }
        }
    )
    return response

# def get_item_AWS(deviceId, timestamp, dynamodb=None):
#     if not dynamodb:
#         if online:
#             dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
#         else:
#             dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")
#
#     table = dynamodb.Table(tableName)
#
#     try:
#         response = table.get_item(Key={'deviceId': deviceId, 'timestamp': timestamp})
#     except ClientError as e:
#         print(e.response['Error']['Message'])
#     else:
#         return response['Item']

#----------------------------------------------------------------------------------------------------------------------#
def now():
    return round(datetime.timestamp(datetime.now()))

def populate_table():
    deviceId = '12CAC94'
    deviceTypeId = '5ff717c325643206e8d57c11'
    seqNumber = 25
    for x in range(num_items):
        timestamp = now() + x - num_items
        time = timestamp
        data = round(1000*math.sin(0.1*x) * math.cos(x))
        item_resp = put_item_AWS(deviceId, timestamp, data, deviceTypeId, seqNumber, time)
        if (x % 10 == 0):
            print("Put " + str(x) + " items")

def create_dataframe():
    columns = ['deviceId', 'timestamp', 'data', 'deviceTypeId', 'seqNumber', 'time']
    index = range(0)
    df = pd.DataFrame(index=index, columns=columns)
    return df

def scan_to_dataframe(df):
    all_items = scan_items_AWS()['Items']
    for i in range(len(all_items)):
        item_dict = {'deviceId': all_items[i]['deviceId'], 'timestamp': datetime.fromtimestamp(int(all_items[i]['timestamp'])),
                    'data': all_items[i]['payload']['data'], 'deviceTypeId': all_items[i]['payload']['deviceTypeId'],
                    'seqNumber': all_items[i]['payload']['seqNumber'], 'time': all_items[i]['payload']['time']}
        df.loc[i] = item_dict
    return df

def last_timestamp(df):
    num_items = len(df.index)
    str = datetime.strftime(df.timestamp[num_items - 1], "%a %b %d %H:%M:%S %Y")
    dt = datetime.strptime(str, "%a %b %d %H:%M:%S %Y")
    timestamp = datetime.timestamp(dt)
    return(round(timestamp))

def append_to_dataframe(df, new_items):

    prev_num_items = len(df.index)

    i = 0
    for new_item in new_items:
        item_dict = {'deviceId': new_item['deviceId'], 'timestamp': datetime.fromtimestamp(int(new_item['timestamp'])),
                    'data': new_item['payload']['data'], 'deviceTypeId': new_item['payload']['deviceTypeId'],
                    'seqNumber': new_item['payload']['seqNumber'], 'time': new_item['payload']['time']}
        df.loc[i+prev_num_items] = item_dict
        i += 1

    num_items = len(df.index)

    return df, num_items

# def plot_items(df):
#     fig = px.line(df, x=df.timestamp, y=df.data, title='Sigfox Data')
#     return fig

#----------------------------------------------------------------------------------------------------------------------#
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
demo = dash.Dash(__name__, external_stylesheets=external_stylesheets)

tableName = 'sigfox_demo'
num_items = 30
online = 0
reset = 1
flag = 1

#----------------------------------------------------------------------------------------------------------------------#
# Reinialize table if reset is True
if reset:
    # Delete the previous table
    delete_sigfox_table_AWS()
    print("Previous sigfox table deleted.")

    # Create the table
    sigfox_table = create_sigfox_table_AWS()
    print("Creating a new sigfox table")
    print("Table status: ", sigfox_table.table_status)

    # Fill the table
    populate_table()

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

# demo.run_server(dev_tools_hot_reload=False)

@demo.callback(Output('sigfox-demo', 'figure'), Input('interval-component', 'n_intervals'))
def update_graph_live(n):

    # Create a DataFrame
    df_empty = create_dataframe()

    # Scan the table to the DataFrame
    df_sigfox = scan_to_dataframe(df_empty)

    # # Set the deviceId and timestamp of the most recent item
    # deviceId = '12CAC94'
    # timestamp = last_timestamp(df_sigfox)
    #
    # # Get all items that are newer than the most recent known item
    # new_items = query_and_project_items_AWS(deviceId, timestamp)

    # # Add the new items to the dataframe
    # if len(new_items):
    #     df_sigfox, num_items = append_to_dataframe(df_sigfox, new_items)
    # new_items.clear()

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

# @demo.callback(Output('sigfox-demo', 'figure'), Input('interval-component', 'n_intervals'))
# def update_graph_live(n):
#
#     print(n)
#     data = {
#         'time': [],
#         'Altitude': []
#     }
#
#     for i in range(180):
#         time = datetime.now() - timedelta(seconds=i*20)
#         alt = random.random()
#         data['Altitude'].append(alt)
#         data['time'].append(time)
#
#     fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)
#
#     fig.append_trace({
#         'x': data['time'],
#         'y': data['Altitude'],
#         'name': 'Altitude',
#         'mode': 'lines+markers',
#         'type': 'scatter'
#     }, 1, 1)
#
#     return fig

# os.system('python add.py')

#----------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    demo.run_server(debug=True)
