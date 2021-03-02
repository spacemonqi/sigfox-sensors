# The update_ functions have to be called in such a way as to update based on changes in the DB - implement this

import pandas as pd
import pickle
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

# Function to get the ld from the csv of all channel,alias,scaling_fact
def get_channels():
    with open('config/channels.csv', mode='r') as csv_file:
        channels_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return channels_ld

# Function to update the csv from the ld of all channel,alias,scaling_fact
def update_channels(filepath, channels_ld):
    with open(filepath, mode='w', newline='') as csv_file:
        fieldnames = ['name', 'alias', 'scaling_fact', 'disabled']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for channel_dict in channels_ld:
            csv_writer.writerow(channel_dict)
        csv_file.close()

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
                if channel['disabled'] == 'Enabled':
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

# Function to return the current page type and instance
def get_current_page_dict():
    with open('temp/tree.txt', 'r') as file:
        checked_global = [current_place.rstrip() for current_place in file.readlines()]
        file.close()

    page_dict = {}
    string = checked_global[0].replace('_', '')
    if (string.find('ch') > -1):
        string, page_dict['ch'] = (string.split('ch'))
    if (string.find('dev') > -1):
        string, page_dict['dev'] = (string.split('dev'))
    if (string.find('loc') > -1):
        string, page_dict['loc'] = (string.split('loc'))
    return page_dict

# Function to write the dcc.Store data
def write_dcc_store_data():
    data = []
    locations_ld = get_locations()
    devices_ld = get_devices()
    channels_ld = get_channels()
    locations_d = {}
    devices_d = {}
    channels_d = {}
    for location in locations_ld:
        for device in devices_ld:
            for channel in channels_ld:
                channels_d[channel['name']] = {'alias': channel['alias'], 'scaling_fact': channel['scaling_fact'], 'disabled': channel['disabled'], 'unit': 'EU'}
            devices_d[device['name']] = {'alias': device['alias'], 'children': channels_d}
        locations_d[location['name']] = {'alias': location['alias'], 'children': devices_d}
    data.append(locations_d)
    file = open(r'temp/dcc_store_data.pkl', 'wb')
    pickle.dump(data, file)
    file.close()

# Function to get the dcc.Store data
def get_dcc_store_data():
    file = open(r'temp/dcc_store_data.pkl', 'rb')
    data = pickle.load(file)
    file.close()

    return data

# Function to update the dcc.Store data
def update_dcc_store_data(data):
    file = open(r'temp/dcc_store_data.pkl', 'wb')
    pickle.dump(data, file)
    file.close()
