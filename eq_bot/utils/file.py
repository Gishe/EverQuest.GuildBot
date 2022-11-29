import os
import shutil
import yaml
import glob
import json

from os import listdir
from os.path import isfile, join

from datetime import datetime, date
from typing import List


def move_file(current_path: str, new_path: str) -> None:
    shutil.move(current_path, new_path)


def make_directory(folder_path: str) -> None:
    isExist = os.path.exists(folder_path)
    if not isExist:
        os.makedirs(folder_path)


def get_files_from_directory(folder_path: str, file_ext: str) -> List[str]:
    return [f for f in listdir(folder_path) if isfile(join(folder_path, f)) and f.endswith(file_ext)]


def read_yaml(file_path: str, expect_found=True) -> dict:
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        if expect_found:
            raise
        pass

def get_latest_modified_file(path_regex: str):
    try:
        return max(glob.iglob(path_regex), key=os.path.getmtime)
    except:
        # TODO: Log error
        pass

def read_json(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.loads(file.read())

def _json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj
    #raise TypeError ("Type %s not serializable" % type(obj))

def write_json(input: dict, file_path):
    with open(file_path, 'w') as file:
        file.write(json.dumps(input, default=_json_serializer))
