import json
import os


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


def merge_jsons_from_dirs(out_path, *in_paths):
    if os.path.exists(out_path):
        os.remove(out_path)

    for in_path in in_paths:
        merge_jsons_from_dir(out_path, in_path)


def _init_merged_content(out_path):
    if os.path.exists(out_path):
        init_content = load_json(out_path)
    else:
        init_content = []

    return init_content


def merge_jsons_from_dir(out_path, in_path):

    merged_jsons = _init_merged_content(out_path)
    for filename in os.listdir(in_path):
        if filename.endswith(".json"):
            json_data = load_json(in_path + '/' + filename)
            assert type(json_data) is list
            merged_jsons = merged_jsons + json_data

    write_json(out_path, merged_jsons)
