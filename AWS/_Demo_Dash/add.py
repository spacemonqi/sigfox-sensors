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

#----------------------------------------------------------------------------------------------------------------------#
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

def scan_items_AWS(dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)
    response = table.scan()
    return response

#----------------------------------------------------------------------------------------------------------------------#
def now():
    return round(datetime.timestamp(datetime.now()))

def add_item():
    deviceId = '12CAC94'
    deviceTypeId = '5ff717c325643206e8d57c11'
    seqNumber = 25
    timestamp = now()
    time = timestamp
    data = round(1000*math.sin(0.1*random.randint(0,30)) * math.cos(random.randint(0,30)))
    item_resp = put_item_AWS(deviceId, timestamp, data, deviceTypeId, seqNumber, time)
    print("Item added")

def create_dataframe():
    columns = ['deviceId', 'timestamp', 'data', 'deviceTypeId', 'seqNumber', 'time']
    index = range(0)
    df = pd.DataFrame(index=index, columns=columns)
    return df

def scan_to_dataframe(df):
    all_items = scan_items_AWS()['Items']
    for i in range(num_items):
        item_dict = {'deviceId': all_items[i]['deviceId'], 'timestamp': datetime.fromtimestamp(int(all_items[i]['timestamp'])),
                    'data': all_items[i]['payload']['data'], 'deviceTypeId': all_items[i]['payload']['deviceTypeId'],
                    'seqNumber': all_items[i]['payload']['seqNumber'], 'time': all_items[i]['payload']['time']}
        df.loc[i] = item_dict
    return df

def last_timestamp(df, num_items):
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

#----------------------------------------------------------------------------------------------------------------------#
tableName = 'sigfox_demo'
num_items = 30
online = 0

#----------------------------------------------------------------------------------------------------------------------#
# Create a DataFrame
df_empty = create_dataframe()

# Scan the table to the DataFrame
df_sigfox = scan_to_dataframe(df_empty)

if __name__ == '__main__':
    while True:
        # Add a new item
        if (input('Add item? y/n\n') == 'y'):
            add_item()

        # Set the deviceId and timestamp of the most recent item
        deviceId = '12CAC94'
        timestamp = last_timestamp(df_sigfox, num_items)
        print(timestamp)

        # Get all items that are newer than the most recent known item
        new_items = query_and_project_items_AWS(deviceId, timestamp) # this has to go to the other app
        print(new_items)

        if len(new_items):
            # Add the new items to the dataframe
            df_sigfox, num_items = append_to_dataframe(df_sigfox, new_items)
            # Plot the data on the graph
            plot_items(sigfoxGraph, df_sigfox)

        print('num_items' + str(num_items) + '\n')
        print(df_sigfox.tail(5))

        new_items.clear()
