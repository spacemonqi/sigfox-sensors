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

import sys


# To run the code using the DynamoDB web service, use find/replace to change
# dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")
# to
# dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

tableName = 'sigfox_demo'
online = False
num_items = 30

def create_sigfox_table(dynamodb=None):
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

def delete_sigfox_table(dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)
    table.delete()

def put_item(deviceId, timestamp, data, deviceTypeId, seqNumber, time, dynamodb=None):
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

def get_item(deviceId, timestamp, dynamodb=None):
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

def scan_items(dynamodb=None):
    if not dynamodb:
        if online:
            dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
        else:
            dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table(tableName)
    response = table.scan()
    return response

if __name__ == '__main__':

    # Delete the table
    delete_sigfox_table()
    print("Previous sigfox table deleted.")

    # Create the table
    print("Creating a new sigfox table")
    sigfox_table = create_sigfox_table()
    print("Table status: ", sigfox_table.table_status)

    # Put all items
    deviceId = '12CAC94'
    deviceTypeId = '5ff717c325643206e8d57c11'
    seqNumber = 25
    time = 1610974881
    for x in range(num_items):
        timestamp = 1610974881 + 60 * x
        data = round(1000*math.sin(0.1*x) * math.cos(x))
        item_resp = put_item(deviceId, timestamp, data, deviceTypeId, seqNumber, time)
        if (x % 10 == 0):
            print("Put " + str(x) + " items")

    # Create a DataFrame
    columns = ['deviceId', 'timestamp', 'data', 'deviceTypeId', 'seqNumber', 'time']
    index = range(0, num_items)
    df_sigfox = pd.DataFrame(index=index, columns=columns)

    # Get all items
    table = scan_items()['Items']
    for i in range(num_items):
        item_dict = {'deviceId': table[i]['deviceId'], 'timestamp': datetime.fromtimestamp(int(table[i]['timestamp'])),
                    'data': table[i]['payload']['data'], 'deviceTypeId': table[i]['payload']['deviceTypeId'],
                    'seqNumber': table[i]['payload']['seqNumber'], 'time': table[i]['payload']['time']}
        df_sigfox.loc[i] = item_dict
    print(df_sigfox.head(10))

    # Plot all items
    fig = go.FigureWidget()
    fig.update_layout(title='Sigfox Demo Data', xaxis_title='Timestamp', yaxis_title='Data')
    fig.add_trace(go.Scatter(x=df_sigfox.timestamp, y=df_sigfox.data, mode='lines+markers', name='Sigfox Data'))
    fig.show()

    while(True):
        # Get an item
        deviceId = '12CAC94'
        timestamp = 1610974881
        item = get_item(deviceId, timestamp)
        if item:
            print("Get item successful")
            pprint(item, sort_dicts=False)
        sleep(1)
