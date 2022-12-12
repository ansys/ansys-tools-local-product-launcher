import json


def check_result_config(path, expected):
    with open(path) as f:
        _config = json.load(f)
    assert _config == expected
