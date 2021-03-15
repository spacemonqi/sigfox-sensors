#!/usr/local/bin/python3

from aws_api import *

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
def now():
    return round(datetime.timestamp(datetime.now()))

def add_item():
    deviceId = '12CAC94'
    timestamp = now()
    data = round(random.randint(0,100))
    temperature = round(random.randint(40, 80))
    humidity = round(np.random.normal(60, 20))
    item_resp = put_item_AWS(online, tableName, deviceId, timestamp, data, temperature, humidity)
    print("Item added")

#----------------------------------------------------------------------------------------------------------------------#
config_dict = {}
with open('config/config.txt', mode='r') as csv_file:
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
