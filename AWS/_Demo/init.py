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
import csv
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
    print("New table created.")
    print('Added ' + str(num_init_items) + ' items.')

#----------------------------------------------------------------------------------------------------------------------#
config_dict = {}
with open('config.txt', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        config_dict[row['setting']] = row['value']
    csv_file.close()

tableName = str(config_dict['tableName'])
num_init_items = int(config_dict['numInitItems'])
online = int(config_dict['online'])
reset = int(config_dict['reset'])

if reset:

    # Check if a previous table exists, delete it if so
    prev_table_exists = 1
    try:
        delete_sigfox_table_AWS()
        print("Deleting previous table...")
    except:
        print("No previous tables exist.")

    # Wait for table to finish deleting, create a new one if done
    while prev_table_exists:
        try:
            sigfox_table = create_sigfox_table_AWS()
            print("Previous table deleted.")
            print("Creating a new sigfox table")
            prev_table_exists = 0
        except:
            print("Previous table status: DELETING" )
            time.sleep(1)

    # Wait for the table to finish creating, populate it if done
    table_created = 0
    while not table_created:
        try:
            populate_table(num_init_items)
            table_created = 1
        except:
            try:
                print("New table status: " + str(sigfox_table.table_status))
            except:
                print("New table status: INITIALIZING")
        time.sleep(1)


os.system('python demo.py')
