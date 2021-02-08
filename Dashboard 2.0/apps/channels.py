import csv

def update_channels(channels_ld):
    with open('apps/config/channels.txt', mode='w', newline='') as csv_file:
        fieldnames = ['channel', 'alias', 'scaling_fact']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for channel_name in channels_ld:
            csv_writer.writerow(channel_name)
        csv_file.close()

def get_channels():
    with open('apps/config/channels.txt', mode='r') as csv_file:
        channels_ld = [{key: value for key, value in row.items()} for row in csv.DictReader(csv_file)]

    return channels_ld

def string_channels():
    channel_name_string = ''
    with open('apps/config/channels.txt', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            channel_name_string += (row['alias'] + ", ")
        csv_file.close()

    return channel_name_string[0:-2]

# channels_ld = [
#     {'channel': 'CH1', 'alias': 'Temperature', 'scaling_fact': 1},
#     {'channel': 'CH2', 'alias': 'Humidity', 'scaling_fact': 1},
#     {'channel': 'CH3', 'alias': 'ADC1', 'scaling_fact': 1},
#     {'channel': 'CH4', 'alias': 'ADC2', 'scaling_fact': 1},
#     {'channel': 'CH5', 'alias': 'CO2', 'scaling_fact': 1},
#     {'channel': 'CH6', 'alias': 'VOC', 'scaling_fact': 1},
# ]
