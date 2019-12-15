# ---------------------------
# D2BS: Item Logger
# ---------------------------
# edit your profile.js to enable item logging, example:
#
# Config.ItemInfo = true; // Log stashed, skipped (due to no space) or sold items.
# Config.ItemInfoQuality = [6, 7, 8];
#
# 6, 7, 8 reprensent item quality to be logged to itemlog file
# lowquality = 1
# normal = 2
# superior = 3
# magic = 4
# set = 5
# rare = 6
# unique = 7
# crafted = 8

import json
import os
import requests
import time
import random
import re
import string

print('Hello!')

# API Webhook
api_url = 'https://webhook.site/e6d80360-ef6f-4b1f-bca0-d55ee96dd5ef'

# path to itemlog.txt (remember to escape)
# c:\users\bob\ ==> should be ==> c:\\users\\bob\\
itemlog = 'P:\\d2bs2\\trunk\\d2bs\\kolbot\\logs\\ItemLog.txt'

# limit of lines in itemlog.txt before we try to empty it
# if this gets too big it might stall your system
itemlog_max_lines = 5000

# sleep time in seconds between each check of itemlog.txt
sleep_between_checks = 30

# actions to post
# valid actions:
# 'Sold', 'Shopped', 'Gambled', 'Dropped', 'No room for'
# 'Kept', 'Field Kept', 'Runeword Kept', 'Cubing Kept'
always_actions = ['Sold', 'Shopped', 'Gambled', 'Dropped',
                  'No room for', 'Kept', 'Field Kept', 'Runeword Kept', 'Cubing Kept']

# == END OF SETTINGS ==


def send_to_api(itemInfo):
    headers = {'Content-Type': 'application/json'}
    data = {}
    data['content'] = itemInfo
    payload = json.dumps(data, indent=4)

    r = requests.post(api_url, data=payload, headers=headers)


def generate_event_id(n):
    id = ''.join(random.SystemRandom().choice(string.ascii_uppercase +
                                              string.ascii_lowercase + string.digits) for _ in range(n))
    return id


def empty_logfile():
    try:
        with open(itemlog, 'w'):
            return True
    except:
        return False


def main():
    current_line = 0

    while True:
        try:
            with open(itemlog) as f:
                lines = f.readlines()
        except:
            print(
                f'[FAIL] failed to open itemlog - retrying in {sleep_between_checks} seconds..')
            time.sleep(sleep_between_checks)
            continue

        if current_line == 0:
            current_line = len(lines)-5
            continue

        for idx, line in enumerate(lines):
            if idx >= current_line:

                regex = r'\[(.+?)\] <(.+?)> <(.+?)> <(.+?)> \((.+?)\) (.+?)$|$'

                match = re.search(regex, line)

                if match:
                    timestamp = match.group(1)
                    character = match.group(2)
                    area = match.group(3)
                    action = match.group(4)
                    quality = match.group(5)

                    item = match.group(6)

                    itemArray = []
                    itemStats = []
                    itemName = ''
                    # Item has additional stats
                    if '|' in item:
                        itemArray = item.split(' | ')

                        # Cost is found and ignored. The item stats start at the third element of the array
                        if 'cost' in itemArray[0].lower():
                            itemName = itemArray[1]
                            itemStats = itemArray[2:]
                            itemStats = list(filter(None, itemStats))
                        # Cost is not found and the item stats begin at the second element of the array
                        else:
                            itemName = itemArray[0]
                            itemStats = itemArray[1:]
                            itemStats = list(filter(None, itemStats))
                    # No additional stats and the item name is present in group 6
                    else:
                        itemName = item

                    # Check to see if the action is enabled to log (Default: All)
                    if action not in always_actions:
                        continue

                    # Generate a unique ID for a Database
                    event_id = generate_event_id(8)

                    # Send to the API
                    send_to_api(itemInfo={
                        "Timestamp": timestamp,
                        "Character": character,
                        "Area": area,
                        "Action": action,
                        "Quality": quality,
                        "ItemName": itemName,
                        "Stats": itemStats,
                        "id": event_id
                    })
                else:
                    print(f'Unable to parse {line}.')

        current_line = len(lines)

        if current_line >= itemlog_max_lines:
            print(f'[WARN] itemlog is {current_line} lines - emptying..')
            if empty_logfile():
                current_line = 0
                print('[OK] itemlog is now empty')
            else:
                print('[FAIL] failed to wipe itemlog!!')

        print(
            f'[OK] done checking itemlog - sleeping for {sleep_between_checks} seconds..')
        time.sleep(sleep_between_checks)


if __name__ == '__main__':
    print(f'[START] Greetings! :-)')
    print(f'[OK] logfile: {itemlog}')
    print(f'------------')
    main()
