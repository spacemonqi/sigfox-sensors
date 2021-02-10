#!/usr/local/bin/python3

from aws_api import *

from datetime import datetime, timedelta
from decimal import Decimal
from pprint import pprint

import pandas as pd
import numpy as np
import random
import math

import json
import time
import sys
import csv
import os

import pdb

breakpoint()

#----------------------------------------------------------------------------------------------------------------------#
def now():
    return round(datetime.timestamp(datetime.now()))

def populate_table(num_init_items):
    deviceId = '12CAC94'
    for x in range(num_init_items):
        timestamp = now() + x - num_init_items
        data = round(random.randint(0,100))
        temperature = round(random.randint(40, 80))
        humidity = round(np.random.normal(60, 20))
        item_resp = put_item_AWS(online, tableName, deviceId, timestamp, data, temperature, humidity)
    print("New table created.")
    print('Added ' + str(num_init_items) + ' items.')

#----------------------------------------------------------------------------------------------------------------------#
config_dict = {}
with open('config/config.txt', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        config_dict[row['setting']] = row['value']
    csv_file.close()

tableName = str(config_dict['tableName'])
num_init_items = int(config_dict['numInitItems'])
online = int(config_dict['online'])

# breakpoint()
#
# delete_sigfox_table_AWS(online, tableName)

# Check if a previous table exists, delete it if so
prev_table_exists = 1
try:
    delete_sigfox_table_AWS(online, tableName)
    print("Deleting previous table...")
except:
    print("No previous tables exist.")

# Wait for table to finish deleting, create a new one if done
while prev_table_exists:
    try:
        sigfox_table = create_sigfox_table_AWS(online, tableName)
        print("Creating a new sigfox table")
        prev_table_exists = 0
    except Exception as e:
        # print(e)
        print("Previous table status: DELETING" )
        time.sleep(1)

# Wait for the table to finish creating, populate it if done
table_created = 0
while not table_created:
    try:
        populate_table(num_init_items)
        table_created = 1
    except Exception as e:
        # print(e)
        try:
            print("New table status: " + str(sigfox_table.table_status))
        except:
            print("New table status: INITIALIZING")
    time.sleep(1)


os.system("python3 demo.py")
