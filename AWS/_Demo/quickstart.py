import csv
import os

file_list = [
    {'setting':'tableName',      'value':'sigfox_demo'},
    {'setting':'numInitItems',   'value':2},
    {'setting':'reset',          'value':1},
    {'setting':'online',         'value':0}
]

with open('config.txt', mode='w') as csv_file:
    fieldnames = ['setting', 'value']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    for item in file_list:
        csv_writer.writerow(item)
    csv_file.close()

os.system('python init.py')
