#Imports=========================================================================================================================#
import pandas as pd
from datetime import datetime
import time
import aws_api



#Functions=======================================================================================================================#
def now():
    return round(datetime.timestamp(datetime.now()))

def write_data_to_csv(filename):
    data_types = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5']
    num_data_types = len(data_types)
    columns = ['location', 'deviceId', 'timestamp', 'data', 'value']
    df = pd.DataFrame(columns=columns)
    all_msgs = aws_api.scan_items_AWS(online, tableName)['Items']
    num_all_msgs = len(all_msgs)
    for i in range(num_all_msgs):
        item_dict = {'location': 'SA', 'deviceId': all_msgs[i]['deviceId'],
                     'timestamp': datetime.fromtimestamp(int(all_msgs[i]['timestamp']/1000))}
        for k in range(num_data_types):
            item_dict['data'] = data_types[k]
            item_dict['value'] = int(all_msgs[i]['payload']['data'][k*4+4:k*4+8], 16)
            df.loc[i * num_data_types + k] = item_dict
    df = df.sort_values(by=['timestamp', 'deviceId', 'data'], ascending=True)
    df.to_csv(filename, index=False, header=True)



#Variables=======================================================================================================================#
tableName = 'Sigfox'
online = 1
sampling_rate = 1  # in seconds



#Loop============================================================================================================================#
while True:
    write_data_to_csv('../data/sensor_data.csv')
    time.sleep(sampling_rate)  # THIS IS VERY BAD - requires a Lambda callback to notify the app when entries are made in DynamoDB
