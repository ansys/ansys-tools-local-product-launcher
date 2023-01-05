import json


def check_result_config(path, expected):
    with open(path) as f:
        config = json.load(f)
    assert config == expected
