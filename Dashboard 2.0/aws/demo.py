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
    data_types = ['ADC', 'CO2', 'VOC', 'Humidity', 'Temperature']
    num_data_types = len(data_types)
    columns = ['deviceId', 'timestamp', 'data', 'value', 'change']
    df = pd.DataFrame(columns=columns)
    all_msgs = scan_items_AWS(online, tableName)['Items']
    num_all_msgs = len(all_msgs)
    for i in range(num_all_msgs):
            item_dict = {'deviceId': all_msgs[i]['deviceId'],
                         'timestamp': datetime.fromtimestamp(int(int(str(all_msgs[i]['timestamp']))/1000+1))} #THIS IS VERY BAD
            for k in range(num_data_types):
                item_dict['data'] = data_types[k]
                item_dict['value'] = int(all_msgs[i]['payload']['data'][k*4+4:k*4+8], 16)
                if (i==0):
                    item_dict['change'] = item_dict['value']
                else:
                    item_dict['change'] = item_dict['value'] - int(df.at[i*num_data_types+k-num_data_types,'value'])
                df.loc[i*num_data_types+k] = item_dict
    df.to_csv(filename, index=False  , header=True)
    last_timestamp = int(int(datetime.timestamp(df.iloc[-1]['timestamp']))*1000)

    return last_timestamp, df

def append_data_to_csv(filename, new_msgs, df):
    num_prev_items = len(df.index)
    data_types = ['Pressure', 'Temperature', 'Humidity']
    fieldnames = ['deviceId', 'timestamp', 'data', 'value', 'change']
    with open(filename, mode='a', newline='') as csv_file:
        for i in range(len(new_msgs)):
            item_dict = {'deviceId': new_msgs[i]['deviceId'],
                         'timestamp': datetime.fromtimestamp(int(int(str(new_msgs[i]['timestamp']))/1000+1))} #THIS IS VERY BAD
            for j in range(len(data_types)):
                item_dict['data'] = data_types[j]
                item_dict['value'] = int(new_msgs[i]['payload']['data'][j*4+2:j*4+6], 16)
                item_dict['change'] = 0
                item_dict['change'] = item_dict['value'] - df.at[num_prev_items + i*3+j-3,'value'] #This program wont work when there are no items to begin with. SO always make sure you have at least 2 messages until this is fixed
                df.loc[num_prev_items + i*3+j] = item_dict
                dictwriter = DictWriter(csv_file, fieldnames=fieldnames)
                dictwriter.writerow(item_dict)
            last_timestamp = int(int(datetime.timestamp(item_dict['timestamp']))*1000)
        csv_file.close()

    return last_timestamp

#----------------------------------------------------------------------------------------------------------------------#
tableName, online = read_params('config/config.txt')

last_timestamp, df_sigfox = write_data_to_csv('data/sensor_data.csv')

# while True:
#     # deviceId = '22229D7'
#     new_msgs = query_and_project_items_AWS(online, tableName, deviceId, last_timestamp)
#     if len(new_msgs):
#         last_timestamp = append_data_to_csv('data/sensor_data.csv', new_msgs, df_sigfox)
#     time.sleep(1)

#----------------------------------------------------------------------------------------------------------------------#
