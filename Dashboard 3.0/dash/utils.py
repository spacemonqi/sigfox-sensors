import pandas as pd
import csv

def get_options(list_data, channel_ld=None):
    dict_list = []
    if channel_ld:
        i = 0
        for item in list_data:
            dict_list.append({'label': channel_ld[i]['alias'], 'value': item})
            i += 1
    else:
        for item in list_data:
            dict_list.append({'label': item, 'value': item})

    return dict_list

def get_df(filename):
    df = pd.read_csv(filename, parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])

    return df

def update_channels(channels_ld):
    with open('config/channels.csv', mode='w', newline='') as csv_file:
        fieldnames = ['channel', 'alias', 'scaling_fact']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for channel_name in channels_ld:
            csv_writer.writerow(channel_name)
        csv_file.close()

def get_channels():
    with open('config/channels.csv', mode='r') as csv_file:
        channels_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return channels_ld

def string_channels():
    channel_name_string = ''
    with open('config/channels.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            channel_name_string += (row['alias'] + ", ")
        csv_file.close()

    return channel_name_string[0:-2]

def update_devices(device_ld):
    with open('config/devices.csv', mode='w', newline='') as csv_file:
        fieldnames = ['deviceid', 'alias']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for device_name in device_ld:
            csv_writer.writerow(device_name)
        csv_file.close()

def get_devices():
    with open('config/devices.csv', mode='r') as csv_file:
        devices_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return devices_ld
