#!/usr/local/bin/python3

from aws_api import *

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
from csv import DictWriter
import sys
import os

import pdb

#----------------------------------------------------------------------------------------------------------------------#
def now():
    return round(datetime.timestamp(datetime.now()))

def read_params(filename):
    config_dict = {}
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            config_dict[row['setting']] = row['value']
        csv_file.close()

    tableName = str(config_dict['tableName'])
    online = int(config_dict['online'])

    return tableName, online

def write_data_to_csv(filename):
    columns = ['deviceId', 'timestamp', 'data', 'temperature', 'humidity']
    index = range(0)
    df = pd.DataFrame(index=index, columns=columns)
    all_items = scan_items_AWS(online, tableName)['Items']
    for i in range(len(all_items)):
        item_dict = {'deviceId': all_items[i]['deviceId'], 'timestamp': all_items[i]['timestamp'],
                    'data': all_items[i]['payload']['data'], 'temperature': all_items[i]['payload']['temperature'],
                    'humidity': all_items[i]['payload']['humidity']}
        df.loc[i] = item_dict
    df.to_csv(filename, index=False, header=True)
    last_timestamp = df.iloc[-1]['timestamp']

    return last_timestamp
    x
def append_data_to_csv(filename, new_items):
    fieldnames = ['deviceId', 'timestamp', 'data', 'temperature', 'humidity']
    with open(filename, mode='a', newline='') as csv_file:
        for new_item in new_items:
            # print(new_item)
            item_dict = {'deviceId': new_item['deviceId'], 'timestamp': new_item['timestamp'],
                        'data': new_item['payload']['data'], 'temperature': new_item['payload']['temperature'],
                        'humidity': new_item['payload']['humidity']}
            dictwriter = DictWriter(csv_file, fieldnames=fieldnames)
            dictwriter.writerow(item_dict)
            last_timestamp = item_dict['timestamp']
        csv_file.close()

    return last_timestamp

#----------------------------------------------------------------------------------------------------------------------#
tableName, online = read_params('config/config.txt')

last_timestamp = write_data_to_csv('data/sensor_data.csv')

while True:
    deviceId = '12CAC94'
    new_items = query_and_project_items_AWS(online, tableName, deviceId, last_timestamp)
    if len(new_items):
        last_timestamp = append_data_to_csv('data/sensor_data.csv', new_items)
    # print('buruh')
    time.sleep(1)

#----------------------------------------------------------------------------------------------------------------------#
