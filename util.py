import os
import re, fnmatch


def read_file(address):
    with open(address, 'r') as f:
        content = f.readall()
        return content


def list_files(directory_address, pattern='*.*'):
    file_names = []
    regex = re.compile(fnmatch.translate(pattern))
    dir_list = os.listdir(directory_address)
    for file in dir_list:
        if regex.match(file):
            file_names.append(file)

