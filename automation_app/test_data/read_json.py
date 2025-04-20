import json


def read_json(jsonFilePath):
    with open(jsonFilePath) as f:
        json_file = json.load(f)

    return json_file
