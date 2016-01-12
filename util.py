import fnmatch
import os
import re


def read_file(address):
    address = os.path.normpath(address)
    with open(address, 'r') as f:
        content = f.read()
        return content


def list_files(directory_address, pattern='*.*'):
    file_names = []
    regex = re.compile(fnmatch.translate(pattern))
    dir_list = os.listdir(directory_address)
    for file in dir_list:
        if regex.match(file):
            file_names.append(file)

