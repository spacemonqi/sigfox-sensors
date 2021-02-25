# The update_ functions have to be called in such a way as to update based on changes in the DB - implement this

import pandas as pd
import csv

# Function to read the data csv file into a dataframe
def get_df(filename):
    df = pd.read_csv(filename, parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])

    return df

# Function to get all value/value or value/label pairs for dropdown options from the ld
def get_options(list_data, ld=None):
    list_data = sorted(list_data)
    dict_list = []
    if ld:
        i = 0
        for item in list_data:
            if ld[i]['alias']:
                dict_list.append({'label': ld[i]['alias'] + ' (' + item + ')', 'value': item})
            else:
                dict_list.append({'label': item, 'value': item})
            i += 1
    else:
        for item in list_data:
            dict_list.append({'label': item, 'value': item})

    return dict_list

# Function to get the ld from the csv of all locations,alias
def get_locations():
    with open('config/locations.csv', mode='r') as csv_file:
        locations_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return locations_ld

# Function to update the csv from the ld of all locations,alias
def update_locations(locations_ld):
    with open('config/locations.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'alias']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for location in locations_ld:
            csv_writer.writerow(location)
        csv_file.close()

# Function to get the ld from the csv of all deviceid,alias
def get_devices():
    with open('config/devices.csv', mode='r') as csv_file:
        devices_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return devices_ld

# Function to update the csv from the ld of all deviceid,alias
def update_devices(devices_ld):
    with open('config/devices.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'alias']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for device_name in devices_ld:
            csv_writer.writerow(device_name)
        csv_file.close()

# Function to update the csv from the ld of all channel,alias,scaling_fact
def update_channels(channels_ld):
    with open('config/channels.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'alias', 'scaling_fact']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for channel_name in channels_ld:
            csv_writer.writerow(channel_name)
        csv_file.close()

# Function to get the ld from the csv of all channel,alias,scaling_fact
def get_channels():
    with open('config/channels.csv', mode='r') as csv_file:
        channels_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return channels_ld

# Function to write a string of channels from the ld of all channel,alias,scaling_fact
def string_channels():
    channel_name_string = ''
    with open('config/channels.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            channel_name_string += (row['alias'] + ", ")
        csv_file.close()

    return channel_name_string[0:-2]

# Function to write the nodes of the navigation tree
def update_tree_nodes(locations_ld, devices_ld, channels_ld):
    # Will later have to change this so it checks which locations have which devices, and which devices have which channels
    tree_children = []
    for location in locations_ld:
        loc_children = []
        for device in devices_ld:
            dev_children = []
            for channel in channels_ld:
                ch_node = {}
                ch_node['value'] = 'loc' + location['name'] + '_' + 'dev' + device['name'] + '_' + channel['name']
                ch_node['label'] = channel['alias']
                dev_children.append(ch_node)
            dev_node = {}
            dev_node['value'] = 'loc' + location['name'] + '_' + 'dev' + device['name']
            dev_node['label'] = device['alias']
            dev_node['children'] = dev_children
            loc_children.append(dev_node)
        loc_node = {}
        loc_node['value'] = 'loc' + location['name']
        loc_node['label'] = location['alias']
        loc_node['children'] = loc_children
        tree_children.append(loc_node)

    return tree_children
