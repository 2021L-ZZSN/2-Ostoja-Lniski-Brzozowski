import json


def load_json(path):
    with open(path, encoding='utf-8') as json_file:
        return json.load(json_file)


def write_json(out_path, data):
    with open(out_path, "w", encoding='utf-8') as write_file:
        json.dump(data, write_file, indent=4)


def append_json(out_path, data):
    json_data: dict = load_json(out_path)
    assert type(json_data) is dict and type(data) is dict, "Can't append json data, if the data is not a dict."
    json_data.update(data)
    write_json(out_path, json_data)