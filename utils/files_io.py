import json


def load_json(path):
    with open(path, encoding='utf-16') as json_file:
        return json.load(json_file)


def write_json(out_path, data):
    with open(out_path, "w", encoding='utf-16') as write_file:
        json.dump(data, write_file, indent=4)
