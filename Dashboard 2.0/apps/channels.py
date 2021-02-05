import csv

def write_channels_to_csv(channel_name_dict):
    with open('apps/config/channels.txt', mode='w', newline='') as csv_file:
        fieldnames = ['channel', 'name']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for channel_name in channel_name_dict:
            csv_writer.writerow(channel_name)
        csv_file.close()

def read_channels_to_string():
    channel_name_string = ''
    with open('apps/config/channels.txt', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            channel_name_string += (row['name'] + ", ")
        csv_file.close()

    return channel_name_string[0:-2]
