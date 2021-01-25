#!/usr/local/bin/python3

import csv
import os


tableName = 'sigfox_demo'
num_init_items = -1
online = -1
reset = -1

# # This needs work - if reset is selected as 0, this is not updated in the file as the csv_writer is never reached
# while not (reset==0 or reset ==1):
#     reset = int(input("Enter '0' to use the previous configuration or '1' to reinitialize: "))

reset = 1

if reset:
    while not (online==0 or online ==1):
        online = int(input("Enter '0' to run locally or '1' to run on the AWS server: "))
    while not(num_init_items>0 and num_init_items<1000):
        num_init_items = int(input("Enter the amount of items for the table: "))

    file_list = [
        {'setting':'tableName',      'value':'sigfox_demo'},
        {'setting':'numInitItems',   'value':num_init_items},
        {'setting':'online',         'value':online},
        {'setting':'reset',          'value':reset}
    ]

    with open('config.txt', mode='w') as csv_file:
        fieldnames = ['setting', 'value']
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for item in file_list:
            csv_writer.writerow(item)
        csv_file.close()

os.system("python3 init.py")
