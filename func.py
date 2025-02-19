from datetime import datetime
import json
from config import LOG_FILE
from pprint import pprint


def system_time():
    now = datetime.now()
    date_time = now.strftime('%d/%m/%Y, %H:%M:%S')
    return 'System time: ' + date_time


def json_read(file):
    try:
        read_json_file = open(file, 'r')
        json_data = json.load(read_json_file)
        read_json_file.close()
        return json_data
    except FileNotFoundError as err:
        print(err)


def json_write(file, data):
    try:
        write_json = json.dumps(data, indent=4)
        write_file = open(file, 'w')
        write_file.write(write_json)
        write_file.close()
    except FileNotFoundError as err:
        print(err)

def log_all(data):
    pprint(data)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f'{data} \n')
    except FileNotFoundError as err:
        print(err)

 # Translate presence status to anything 
def presence_translate(data):
    online = ''
    away = 'away'
    busy = 'busy'
    return data.replace(' - online', '').replace('away', away).replace('busy', busy)


def present(data):
    return data == 'online' or data == 'away' or data == 'busy'
