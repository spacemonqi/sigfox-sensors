#!/usr/local/bin/python3

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import boto3

from datetime import datetime, timedelta
from decimal import Decimal
from pprint import pprint
import json

import math
import random
import pandas as pd
import numpy as np
from collections import deque

import time
import csv
import sys
import os

import pdb

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
    columns = ['deviceId', 'timestamp', 'data', 'temperature', 'humidity', 'time']
    index = range(0)
    df = pd.DataFrame(index=index, columns=columns)
    all_items = scan_items_AWS()['Items']
    for i in range(len(all_items)):
        item_dict = {'deviceId': all_items[i]['deviceId'], 'timestamp': all_items[i]['timestamp'],
                    'data': all_items[i]['payload']['data'], 'temperature': all_items[i]['payload']['temperature'],
                    'humidity': all_items[i]['payload']['humidity']}
        df.loc[i] = item_dict
    return df

def last_timestamp(df):
    num_items = len(df.index)
    timestamp = int(str(df.timestamp[num_items-1]))
    return timestamp

def append_to_dataframe(new_items):

    num_items = len(df_sigfox.index)

    i = 0
    for new_item in new_items:
        item_dict = {'deviceId': new_item['deviceId'], 'timestamp': new_item['timestamp'],
                    'data': new_item['payload']['data'], 'temperature': new_item['payload']['temperature'],
                    'humidity': new_item['payload']['humidity']}
        df_sigfox.loc[i+num_items] = item_dict
        i += 1

#----------------------------------------------------------------------------------------------------------------------#
config_dict = {}
with open('config.txt', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        config_dict[row['setting']] = row['value']
    csv_file.close()

tableName = str(config_dict['tableName'])
online = int(config_dict['online'])

df_sigfox = scan_to_dataframe()
print(df_sigfox.head(10))

breakpoint()

X = deque()
Y = deque()
for i in range(len(df_sigfox.index)):
    X.append(datetime.fromtimestamp(int(df_sigfox['timestamp'][i])))
    Y.append(df_sigfox['data'][i])


# X.append(datetime.fromtimestamp(now()))
# num_items = len(df_sigfox.index)
# Y.append(df_sigfox['data'][num_items-1])
#
# with open('config.txt', mode='w') as csv_file:
#     fieldnames = ['setting', 'value']
#     csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#     csv_writer.writeheader()
#     for item in file_list:
#         csv_writer.writerow(item)
#     csv_file.close()

#----------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    pass
