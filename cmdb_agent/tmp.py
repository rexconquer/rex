import commands
import os
import re
import logging


try:
    import json
except ImportError:
    import simplejson as json

def df():
    COMMAND = 'df -h'
    return commands.getoutput(COMMAND)

def dfToJson(stats):
    lines = str(stats).splitlines()
    # count number of headers
    array = []
    i = 1
    while i < len(lines):
        disk = dict()
        if len(lines[i].strip().split()) < 6:
            disk['Filesystem'] = lines[i].strip()
            disk['Size'] = lines[i+1].strip().split()[0]
            disk['Used'] = lines[i+1].strip().split()[1]
            disk['Avail'] = lines[i+1].strip().split()[2]
            disk['Use%'] = lines[i+1].strip().split()[3]
            disk['Mounted_on'] = lines[i+1].strip().split()[4]
            i = i +2
            array.append(disk)
        else:
            disk['Filesystem'] = lines[i].strip().split()[0]
            disk['Size'] = lines[i].strip().split()[1]
            disk['Used'] = lines[i].strip().split()[2]
            disk['Avail'] = lines[i].strip().split()[3]
            disk['Use%'] = lines[i].strip().split()[4]
            disk['Mounted_on'] = lines[i].strip().split()[5]
            i = i +1
            array.append(disk)

    return array

def main(path, C=None, name='df'):
    data = df()
    # Only valid with python > 2.5 ...... Dammit
    # with open('data.txt', 'w') as outfile:
    #     json.dump(data, outfile)
    dataJson = open(os.path.join(path, name +'.json'), 'w')
    dataRaw = open(os.path.join(path, name +'.txt'), 'w')
    try:
        json.dump(dfToJson(data), dataJson, indent=4)
        dataRaw.write(data)
    finally:
        dataJson.close()
        dataRaw.close()

if __name__ == "__main__":
    main('.')
