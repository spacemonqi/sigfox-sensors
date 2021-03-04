#Imports=========================================================================================================================#
import pandas as pd
import pickle
import csv
# from functools import reduce
# from operator import getitem



#Data============================================================================================================================#
# Function to read the data csv file into a dataframe
def get_df(filename):
    df = pd.read_csv(filename, parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])

    return df



#dccStore========================================================================================================================#
# Function to write the dcc.Store data
def write_dcc_store_data():
    # data = []  # There is some weird problem with this code
    # locations_ld = get_locations_old()
    # devices_ld = get_devices_old()
    # channels_ld = get_channels_old()
    # locations_d = {}
    # devices_d = {}
    # channels_d = {}
    # for location in locations_ld:
    #     for device in devices_ld:
    #         for channel in channels_ld:
    #             channels_d[channel['name']] = {'alias': channel['alias'], 'scaling_fact': channel['scaling_fact'], 'disabled': channel['disabled'], 'unit': ''}
    #         devices_d[device['name']] = {'alias': device['alias'], 'children'+str(device['name']): channels_d}
    #     locations_d[location['name']] = {'alias': location['alias'], 'children': devices_d}
    # data.append(locations_d)

    # data = []  # There is some weird problem with this code
    # locations_l = ['SA']
    # devices_l = ['22229D7', '22229D9']
    # channels_l = ['ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6']
    # locations_d = {}
    # devices_d = {}
    # channels_d = {}
    # for location in locations_l:
    #     for device in devices_l:
    #         for channel in channels_l:
    #             channels_d[channel] = {'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''}
    #         devices_d[device] = {'alias': '', 'children': channels_d}
    #     locations_d[location] = {'alias': '', 'children': devices_d}
    # data.append(locations_d)

    data = []
    locations_l = ['SA']
    devices_l = ['22229D7', '22229D9']
    locations_d = {}
    devices_d = {}
    for location in locations_l:
        for device in devices_l:
            devices_d[device] = {
                'alias': '', 'children': {
                    'ch1': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch2': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch3': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch4': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch5': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                }
            }
        locations_d[location] = {'alias': 'South Africa', 'children': devices_d}
    data.append(locations_d)

    # data = [{'SA': {
    #     'alias': 'South Africa', 'children': {
    #         '22229D7': {
    #             'alias': 'DevKit1', 'children': {
    #                 'ch1': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch2': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch3': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch4': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch5': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch6': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 }
    #             }
    #         },
    #         '22229D9': {
    #             'alias': 'DevKit2', 'children': {
    #                 'ch1': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch2': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch3': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch4': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch5': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 },
    #                 'ch6': {
    #                     'alias': '', 'scaling_fact': '', 'disabled': 'Enabled', 'unit': ''
    #                 }
    #             }
    #         }
    #     }
    # }}]

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

# write_dcc_store_data()
# data = get_dcc_store_data()
# print('\ndata')
# print(data)
# # del data[0]['SA']['children']['22229D7']['children']['ch6']['unit']
# data[0]['SA']['children']['22229D9']['children']['ch5']['unit'] = 'XXXXXXXXXXXXXXXXXXXXXX'
# print('\ndata')
# print(data)



#LD_new==========================================================================================================================#
# Function to get the ld from the csv of all location,alias,scaling_fact
def get_locations():
    data = get_dcc_store_data()
    locations_ld = []
    locations = data[0]
    for location in locations:
        locations_ld.append({'name': location,
                            'alias': locations[location]['alias']})

    return locations_ld

# Function to get the ld from the csv of all channel,alias,scaling_fact
def get_devices(location=None):
    data = get_dcc_store_data()
    devices_ld = []
    if location:
        devices = data[0][location]['children']
        for device in devices:
            devices_ld.append({'name': device,
                               'alias': devices[device]['alias']})
    else:
        devices = data[0][location]['children']
        for device in devices:
            devices_ld.append({'name': device,
                               'alias': devices[device]['alias']})

    return devices_ld

# Function to get the ld from the csv of all channel,alias,scaling_fact
def get_channels(location=None, device=None):
    data = get_dcc_store_data()
    channels_ld = []
    if location and device:
        channels = data[0][location]['children'][device]['children']
        for channel in channels:
            channels_ld.append({'name': channel,
                                'alias': channels[channel]['alias'],
                                'scaling_fact': channels[channel]['scaling_fact'],
                                'disabled': channels[channel]['disabled'],
                                'unit': channels[channel]['unit']})

    return channels_ld

# print('\n\n')
# print(get_locations_from_data())
# print('\n\n')
# print(get_devices_from_data('SA'))
# print('\n\n')
# print(get_channels_from_data('SA', '22229D9'))



#LD_old==========================================================================================================================#
# Function to get the ld from the csv of all locations,alias
def get_locations_old():
    with open('config/locations.csv', mode='r') as csv_file:
        locations_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return locations_ld

# Function to update the csv from the ld of all locations,alias
def update_locations_old(locations_ld):
    with open('config/locations.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'alias']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for location in locations_ld:
            csv_writer.writerow(location)
        csv_file.close()

# Function to get the ld from the csv of all deviceid,alias
def get_devices_oLD_old():
    with open('config/devices.csv', mode='r') as csv_file:
        devices_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return devices_ld

# Function to update the csv from the ld of all deviceid,alias
def update_devices_old(devices_ld):
    with open('config/devices.csv', mode='w', newline='') as csv_file:
        fieldnames = ['name', 'alias']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for device_name in devices_ld:
            csv_writer.writerow(device_name)
        csv_file.close()

# Function to get the ld from the csv of all channel,alias,scaling_fact
def get_channels_old():
    with open('config/channels.csv', mode='r') as csv_file:
        channels_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]
        csv_file.close()

    return channels_ld

# Function to update the csv from the ld of all channel,alias,scaling_fact
def update_channels_old(filepath, channels_ld):
    with open(filepath, mode='w', newline='') as csv_file:
        fieldnames = ['name', 'alias', 'scaling_fact', 'disabled']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for channel_dict in channels_ld:
            csv_writer.writerow(channel_dict)
        csv_file.close()

# # Function to write a string of channels from the ld of all channel,alias,scaling_fact
# def string_channels():
#     channel_name_string = ''
#     with open('config/channels.csv', mode='r') as csv_file:
#         csv_reader = csv.DictReader(csv_file)
#         for row in csv_reader:
#             channel_name_string += (row['alias'] + ", ")
#         csv_file.close()
#
#     return channel_name_string[0:-2]
#



#Utilities=======================================================================================================================#
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



#Tree============================================================================================================================#
# Function to write the nodes of the navigation tree
def update_tree_nodes(data):
    tree_children = []
    locations = data[0]
    for location in locations:
        loc_children = []
        devices = locations[location]['children']
        for device in devices:
            dev_children = []
            channels = devices[device]['children']
            for channel in channels:
                if channels[channel]['disabled'] == 'Enabled':
                    ch_node = {}
                    ch_node['value'] = 'loc' + location + '_' + 'dev' + device + '_' + channel
                    ch_node['label'] = channels[channel]['alias'] if channels[channel]['alias'] else channel
                    dev_children.append(ch_node)
            dev_node = {}
            dev_node['value'] = 'loc' + location + '_' + 'dev' + device
            dev_node['label'] = devices[device]['alias'] if devices[device]['alias'] else device
            dev_node['children'] = dev_children
            loc_children.append(dev_node)
        loc_node = {}
        loc_node['value'] = 'loc' + location
        loc_node['label'] = locations[location]['alias']
        loc_node['children'] = loc_children
        tree_children.append(loc_node)

    return tree_children



#Tree_old============================================================================================================================#
# Function to write the nodes of the navigation tree
def update_tree_nodes_old(locations_ld, devices_ld, channels_ld):
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



#Views===========================================================================================================================#
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
