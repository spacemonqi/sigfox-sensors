#Imports=========================================================================================================================#
import pandas as pd
import pickle



#Data============================================================================================================================#
# Read the data csv file into a dataframe
def get_df(filename):
    df = pd.read_csv(filename, parse_dates=True)
    df.index = pd.to_datetime(df['timestamp'])

    return df



#Lists of Dictionaries===========================================================================================================#
# Get a location list of dictionaries from store_data
def get_locations():
    data = get_store_data()
    locations_ld = []
    locations = data[0]
    for location in locations:
        locations_ld.append({'name': location, 'alias': locations[location]['alias']})

    return locations_ld

# Get a device list of dictionaries from store_data
def get_devices(location=None):
    data = get_store_data()
    devices_ld = []
    if location:
        devices = data[0][location]['children']
        for device in devices:
            devices_ld.append({'name': device, 'alias': devices[device]['alias']})
    else:
        devices = data[0][location]['children']
        for device in devices:
            devices_ld.append({'name': device, 'alias': devices[device]['alias']})

    return devices_ld

# Get a channel list of dictionaries from store_data
def get_channels(location=None, device=None):
    data = get_store_data()
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



#Store Data - this tracks the location/device/channel hierarchy and children=====================================================#
# Write (reset) the store data
def write_store_data():

    data = []
    locations_l = ['Default_Location']
    devices_l = ['Default_Device']
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
        locations_d[location] = {'alias': location, 'children': devices_d}
    data.append(locations_d)

    file = open(r'temp/dcc_store_data.pkl', 'wb')
    pickle.dump(data, file)
    file.close()

# Get the store data
def get_store_data():
    file = open(r'temp/dcc_store_data.pkl', 'rb')
    flag = False
    while not flag:
        try:
            data = pickle.load(file)
            flag = True
        except EOFError:
            pass
    file.close()

    return data

# Update the store data
def update_store_data(data):
    file = open(r'temp/dcc_store_data.pkl', 'wb')
    pickle.dump(data, file)
    file.close()

# Add locations/devices to the store data
def add_device_store_data():
    df = get_df('../data/sensor_data.csv')
    data = get_store_data()
    devices_l = sorted(df['deviceId'].unique()),

    for device in devices_l[0]:
        location = df.loc[df['deviceId'] == device]['location'][0]
        if not data[0].get(location):
            data[0][location] = {'alias': location, 'children': {}}
        if not data[0][location]['children'].get(device):
            device_d = {
                'alias': '', 'children': {
                    'ch1': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch2': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch3': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch4': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                    'ch5': {'alias': '', 'scaling_fact': '1', 'disabled': 'Enabled', 'unit': ''},
                }
            }
            data[0][location]['children'][device] = device_d
            if data[0].get('Default_Location'): del data[0]['Default_Location']
            update_store_data(data)



#Tree============================================================================================================================#
# Write the nodes of the navigation tree from the store data
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



#Views===========================================================================================================================#
# Get the current page type and instance
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
