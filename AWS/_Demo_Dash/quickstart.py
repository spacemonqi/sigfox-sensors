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

#----------------------------------------------------------------------------------------------------------------------#
def now():
    return round(datetime.timestamp(datetime.now()))

def populate_table(num_init_items):
    deviceId = '12CAC94'
    deviceTypeId = '5ff717c325643206e8d57c11'
    seqNumber = 25
    for x in range(num_init_items):
        timestamp = now() + x - num_init_items
        time = timestamp
        data = round(1000*math.sin(0.1*x) * math.cos(x))
        item_resp = put_item_AWS(deviceId, timestamp, data, deviceTypeId, seqNumber, time)
        if (x % 10 == 0):
            print("Put " + str(x) + " items")

#----------------------------------------------------------------------------------------------------------------------#
tableName = 'sigfox_demo'
num_init_items = 9
online = 0
reset = 1

if reset:
    file = open("config.txt", 'w')
    file.write(tableName + '\n')
    file.write(str(online) + '\n')
    file.close()

    # Delete the previous table
    delete_sigfox_table_AWS()
    print("Previous sigfox table deleted.")

    # Create the table
    sigfox_table = create_sigfox_table_AWS()
    print("Creating a new sigfox table")
    print("Table status: ", sigfox_table.table_status)

    # Fill the table
    populate_table(num_init_items)

os.system('python demo.py')
