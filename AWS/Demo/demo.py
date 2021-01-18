from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import boto3

from datetime import datetime
from decimal import Decimal
from pprint import pprint
import json

import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go

import time
import sys

#----------------------------------------------------------------------------------------------------------------------#
tableName = 'sigfox_demo'
num_items = 30
online = False
reset = False
show = False

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

def get_item_AWS(deviceId, timestamp, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)

    try:
        response = table.get_item(Key={'deviceId': deviceId, 'timestamp': timestamp})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']

def query_and_project_items_AWS(deviceId, last_timestamp, dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)

    # Expression attribute names can only reference items in the projection expression.
    response = table.query(
        ProjectionExpression="#id, #ts",
        ExpressionAttributeNames={'#id': 'deviceId', '#ts': 'timestamp'},
        KeyConditionExpression=Key('deviceId').eq(deviceId) & Key('timestamp').between(last_timestamp, 2147483647)
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
def populate_table(now):
    deviceId = '12CAC94'
    deviceTypeId = '5ff717c325643206e8d57c11'
    seqNumber = 25
    time = now
    for x in range(num_items):
        timestamp = now + 60 * x
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
    table = scan_items_AWS()['Items']
    for i in range(num_items):
        item_dict = {'deviceId': table[i]['deviceId'], 'timestamp': datetime.fromtimestamp(int(table[i]['timestamp'])),
                    'data': table[i]['payload']['data'], 'deviceTypeId': table[i]['payload']['deviceTypeId'],
                    'seqNumber': table[i]['payload']['seqNumber'], 'time': table[i]['payload']['time']}
        df.loc[i] = item_dict
    return df

def init_plot():
    fig = go.FigureWidget()
    fig.update_layout(title='Sigfox Demo Data', xaxis_title='Timestamp', yaxis_title='Data')
    return fig

def plot_items(fig, df_sigfox):
    fig.add_trace(go.Scatter(x=df_sigfox.timestamp, y=df_sigfox.data, mode='lines+markers', name='Sigfox Data'))
    if show:
        fig.show()

def last_timestamp(df):
    str = datetime.strftime(df.timestamp[num_items - 1], "%a %b %d %H:%M:%S %Y")
    dt = datetime.strptime(str, "%a %b %d %H:%M:%S %Y")
    timestamp = datetime.timestamp(dt)
    return(round(timestamp)+1)

def append_to_dataframe(df, new_items):
    print(df.tail(20))
    prev_num_items = len(df.index)
    print('ni ' + str(num_items))
    print('pni ' + str(prev_num_items))
    for i in range(prev_num_items, num_items):
        print(new_items[i-prev_num_items])
        print(i)
        input()
        df.loc[i] = new_items[i-prev_num_items]
    print(df.tail(50))

#----------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':

    # Obtain the current timestamp
    now = round(datetime.timestamp(datetime.now()))

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
        populate_table(now)

    # Create a DataFrame
    df_empty = create_dataframe()

    # Scan the table to the DataFrame
    df_sigfox = scan_to_dataframe(df_empty)

    # Initialize the graph
    sigfoxGraph = init_plot()

    # Plot the data on the graph
    plot_items(sigfoxGraph, df_sigfox)

    while(True):

        # Set the deviceId and timestamp of the most recent item
        deviceId = '12CAC94'
        timestamp = last_timestamp(df_sigfox)

        # Get all items that are newer than the most recent known item
        new_items = query_and_project_items_AWS(deviceId, now) # change now to timestamp

        if new_items:
            print(new_items) #what happens to the data????

            # Update the number of items
            # num_items += len(new_items)

            # Add the new items to the dataframe
            # append_to_dataframe(df_sigfox, new_items)

        sys.exit()

        # time.sleep(1)
