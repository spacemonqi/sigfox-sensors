from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import boto3

from decimal import Decimal
from pprint import pprint
import json

import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# To run the code using the DynamoDB web service, use find/replace to change
# dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")
# to
# dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

def create_sigfox_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.create_table(
        TableName='sigfox_demo',
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
        }
    )
    return table

def delete_sigfox_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table('sigfox_demo')
    table.delete()

def put_item(deviceId, timestamp, data, deviceTypeId, seqNumber, time, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table('sigfox_demo')
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
        dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")

    table = dynamodb.Table('sigfox_demo')

    try:
        response = table.get_item(Key={'deviceId': deviceId, 'timestamp': timestamp})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']

def scan_items(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('sigfox_demo')
    response = table.scan()
    return response

if __name__ == '__main__':

    # # Create the table
    # sigfox_table = create_sigfox_table()
    # print("Table status: ", sigfox_table.table_status)

    # # Delete the table
    # delete_sigfox_table()
    # print("Sigfox table deleted.")

    # # Put all items
    # deviceId = '12CAC94'
    # timestamp = 1610442045307
    # data = 2
    # deviceTypeId = '5ff717c325643206e8d57c11'
    # seqNumber = 25
    # time = 1610442043
    # for x in range(100):
    #     timestamp = 161044204530+x
    #     data = round(1000*math.sin(0.1*x) * math.cos(x))
    #     item_resp = put_item(deviceId, timestamp, data, deviceTypeId, seqNumber, time)
    #     print("Put item successful")
    #     # pprint(item_resp, sort_dicts=False)

    # Create a DataFrame
    columns = ['deviceId', 'timestamp', 'data', 'deviceTypeId', 'seqNumber', 'time']
    index = range(0, 100)
    df_sigfox = pd.DataFrame(index=index, columns=columns)
    # print(df_sigfox.head())

    # Get all items
    table = scan_items()['Items']
    for i in range(100):
        item_dict = {'deviceId': table[i]['deviceId'], 'timestamp': table[i]['timestamp'],
                    'data': table[i]['payload']['data'], 'deviceTypeId': table[i]['payload']['deviceTypeId'],
                    'seqNumber': table[i]['payload']['seqNumber'], 'time': table[i]['payload']['time']}
        df_sigfox.loc[i] = item_dict
    print(df_sigfox.head(10))

    # Plot the data
    input("Press Enter")
    fig = go.FigureWidget()
    fig.update_layout(title='Sigfox Demo Data', xaxis_title='Timestamp', yaxis_title='Data')
    fig.add_trace(go.Scatter(x=df_sigfox.timestamp, y=df_sigfox.data, mode='lines+markers', name='Sigfox Data'))
    fig.show()

    # input("Press Enter")
    # for i in range(20):
    #     item_dict = {'deviceId': '12CAC94', 'timestamp': 161044204530+i, 'data': i**3, 'deviceTypeId': '5ff717c325643206e8d57c11', 'seqNumber' : 25, 'time' : 161044204530+i}
    #     df_sigfox.loc[i] = item_dict
    # fig.add_trace(go.Scatter(x=df_sigfox.timestamp, y=df_sigfox.data, mode='lines+markers', name='Sigfox Data'))
    # fig.show()

    # # Get an item
    # deviceId = '12CAC94'
    # timestamp = 1610442045307
    # item = get_item(deviceId, timestamp)
    # if item:
    #     print("Get item successful")
    #     pprint(item, sort_dicts=False)
    #
    #
    # # Add an item to the DataFrame
    # item_dict = {'deviceId': deviceId, 'timestamp': timestamp, 'data': data, 'deviceTypeId': deviceTypeId, 'seqNumber' : seqNumber, 'time' : time}
    # df_sigfox.loc[1] = item_dict
