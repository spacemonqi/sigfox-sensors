from decimal import Decimal
from pprint import pprint
import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

import pandas as pd
import numpy as np
import chart_studio.plotly as py
import cufflinks as cf
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

from matplotlib import pyplot as plt

# To run the code using the DynamoDB web service, change the line
# dynamodb = boto3.resource('dynamodb',endpoint_url="http://localhost:8000")
# to
# dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

def create_sigfox_table(dynamodb=None):
    if not dynamodb:
        # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

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
        # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

    table = dynamodb.Table('sigfox_demo')
    table.delete()

def put_item(deviceId, timestamp, data, deviceTypeId, seqNumber, time, dynamodb=None):
    if not dynamodb:
        # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

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
        # dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

    table = dynamodb.Table('sigfox_demo')

    try:
        response = table.get_item(Key={'deviceId': deviceId, 'timestamp': timestamp})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return response['Item']

if __name__ == '__main__':

    # # Create the table
    # sigfox_table = create_sigfox_table()
    # print("Table status: ", sigfox_table.table_status)

    # # Delete the table
    # delete_sigfox_table()
    # print("Sigfox table deleted.")

    # Add an item
    deviceId = '12CAC94'
    timestamp = 1610442045307
    data = 2
    deviceTypeId = '5ff717c325643206e8d57c11'
    seqNumber = 25
    time = 1610442043
    item_resp = put_item(deviceId, timestamp, data, deviceTypeId, seqNumber, time)
    print("Put item successful")
    pprint(item_resp, sort_dicts=False)

    # Read an item
    item = get_item(deviceId, timestamp)
    if item:
        print("Get item successful")
        pprint(item, sort_dicts=False)

    df_stocks = px.data.stocks()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_stocks.date, y=df_stocks.AAPL, mode='lines', name='Apple'))
    fig.add_trace(go.Scatter(x=df_stocks.date, y=df_stocks.AMZN, mode='lines+markers', name='Amazon'))
    fig.add_trace(go.Scatter(x=df_stocks.date, y=df_stocks.GOOG, mode='lines+markers', name='Google', line=dict(color='firebrick', width=2, dash='dashdot')))
    fig.update_layout(title='Stock Price Data 2018 - 2020', xaxis_title='Price', yaxis_title='Date')
    fig.show()
    print(df_stocks)

    # arr_1 = np.random.randn(50,4)
    # df_1 = pd.DataFrame(arr_1, columns=['A','B','C','D'])
    # df_1.head()
    # df_1.plot()
    # plt.show()

    # fig = px.line(df_stocks, x='date', y='GOOG', labels={'x': 'Date', 'y':'Price'})
    # fig.show()
    # fig = px.line(df_stocks, x='date', y=['GOOG','AAPL'], labels={'x': 'Date', 'y':'Price'}, title='Apple vs Google')
    # fig.show()
