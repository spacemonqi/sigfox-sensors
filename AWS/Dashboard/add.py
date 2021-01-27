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
import numpy as np

import time
import csv
import sys

#----------------------------------------------------------------------------------------------------------------------#
def put_item_AWS(deviceId, timestamp, data, temperature, humidity, dynamodb=None):
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
                'temperature': temperature,
                'humidity' : humidity
            }
        }
    )
    return response

#----------------------------------------------------------------------------------------------------------------------#
def now():
    return round(datetime.timestamp(datetime.now()))

def add_item():
    deviceId = '12CAC94'
    timestamp = now()
    data = round(1000*math.sin(0.1*random.randint(0,30)) * math.cos(random.randint(0,30)))
    temperature = round(random.randint(40, 80))
    humidity = round(np.random.normal(60, 20))
    item_resp = put_item_AWS(deviceId, timestamp, data, temperature, humidity)
    print("Item added")

#----------------------------------------------------------------------------------------------------------------------#
config_dict = {}
with open('config.txt', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        config_dict[row['setting']] = row['value']
    csv_file.close()

tableName = str(config_dict['tableName'])
online = int(config_dict['online'])

#----------------------------------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    while True:
        # Add a new item
        input('Press Enter to add an item')
        add_item()
