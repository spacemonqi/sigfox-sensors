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
    data_types = ['pressure', 'temperature', 'humidity']
    columns = ['deviceId', 'timestamp', 'data', 'value', 'change']
    index = range(0)
    df = pd.DataFrame(index=index, columns=columns)
    all_msgs = scan_items_AWS(online, tableName)['Items']
    for i in range(len(all_msgs)):
            item_dict = {'deviceId': all_msgs[i]['deviceId'], 'timestamp': int(str(all_msgs[i]['timestamp']))}
            for j in range(len(data_types)):
                item_dict['data'] = data_types[j]
                item_dict['value'] = int(all_msgs[i]['payload']['data'][j*4+2:j*4+6], 16)
                # breakpoint()
                if (i==0):
                    item_dict['change'] = item_dict['value']
                else:
                    item_dict['change'] = item_dict['value'] - df.at[i*3+j-3,'value']
                df.loc[i*3+j] = item_dict
    df.to_csv(filename, index=True  , header=True)
    last_timestamp = df.iloc[-1]['timestamp']

    return last_timestamp

def append_data_to_csv(filename, new_items):
    fieldnames = ['deviceId', 'timestamp', 'data', 'temperature', 'humidity']
    with open(filename, mode='a', newline='') as csv_file:
        for new_item in new_items:
            # print(new_item)
            item_dict = {'deviceId': new_item['deviceId'], 'timestamp': int(str(new_item['timestamp'])),
                        'data': new_item['payload']['data'], 'temperature': new_item['payload']['temperature'],
                        'humidity': new_item['payload']['humidity']}
            dictwriter = DictWriter(csv_file, fieldnames=fieldnames)
            dictwriter.writerow(item_dict)
            last_timestamp = int(str(item_dict['timestamp']))
        csv_file.close()

    return last_timestamp

#----------------------------------------------------------------------------------------------------------------------#
tableName, online = read_params('config/config.txt')

last_timestamp = write_data_to_csv('data/sensor_data.csv')

# while True:
#     deviceId = '22229D7'
#     new_items = query_and_project_items_AWS(online, tableName, deviceId, last_timestamp)
#     breakpoint()
#     if len(new_items):
#         last_timestamp = append_data_to_csv('data/sensor_data.csv', new_items)
#     time.sleep(1)

#----------------------------------------------------------------------------------------------------------------------#
