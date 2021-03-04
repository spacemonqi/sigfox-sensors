#Imports=========================================================================================================================#
import pandas as pd
from datetime import datetime
import time
import csv
import aws_api



#Functions=======================================================================================================================#
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
    data_types = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5']
    # data_types = ['ch1']
    num_data_types = len(data_types)
    columns = ['location', 'deviceId', 'timestamp', 'data', 'value']
    df = pd.DataFrame(columns=columns)
    all_msgs = aws_api.scan_items_AWS(online, tableName)['Items']
    num_all_msgs = len(all_msgs)
    for i in range(num_all_msgs):
        item_dict = {'location': 'SA', 'deviceId': all_msgs[i]['deviceId'],
                     'timestamp': datetime.fromtimestamp(int(str(all_msgs[i]['timestamp'])))}
        for k in range(num_data_types):
            item_dict['data'] = data_types[k]
            item_dict['value'] = int(all_msgs[i]['payload']['data'][k*4+4:k*4+8], 16)
            df.loc[i * num_data_types + k] = item_dict
    df = df.sort_values(by=['timestamp', 'deviceId', 'data'], ascending=True)
    df.to_csv(filename, index=False, header=True)

# def append_data_to_csv(filename, new_msgs, df): # create a global secondary index to query by sort key only
#     num_prev_items = len(df.index)
#     data_types = ['Pressure', 'Temperature', 'Humidity']
#     fieldnames = ['deviceId', 'timestamp', 'data', 'value', 'change']
#     with open(filename, mode='a', newline='') as csv_file:
#         for i in range(len(new_msgs)):
#             item_dict = {'deviceId': new_msgs[i]['deviceId'],
#                          'timestamp': datetime.fromtimestamp(int(int(str(new_msgs[i]['timestamp']))/1000+1))} #THIS IS VERY BAD
#             for j in range(len(data_types)):
#                 item_dict['data'] = data_types[j]
#                 item_dict['value'] = int(new_msgs[i]['payload']['data'][j*4+2:j*4+6], 16)
#                 item_dict['change'] = 0
#                 item_dict['change'] = item_dict['value'] - df.at[num_prev_items + i*3+j-3,'value'] # THis doesnt work for the first items and This program wont work when there are no items to begin with. SO always make sure you have at least 2 messages until this is fixed
#                 df.loc[num_prev_items + i*3+j] = item_dict
#                 dictwriter = DictWriter(csv_file, fieldnames=fieldnames)
#                 dictwriter.writerow(item_dict)
#             last_timestamp = int(int(datetime.timestamp(item_dict['timestamp']))*1000)
#         csv_file.close()
#
#    return last_timestamp



#Variables=======================================================================================================================#
tableName, online = read_params('config/config.txt')



#Loop============================================================================================================================#
while True:
    write_data_to_csv('../data/sensor_data.csv')
    time.sleep(1)                                                           # THIS IS VERY BAD

# while True:
#     # deviceId = '22229D7'
#     new_msgs = query_and_project_items_AWS(online, tableName, deviceId, last_timestamp)
#     if len(new_msgs):
#         last_timestamp = append_data_to_csv('data/sensor_data.csv', new_msgs, df_sigfox)
#     time.sleep(1)
