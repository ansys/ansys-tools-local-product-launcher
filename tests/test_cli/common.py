import json
from unittest.mock import Mock

from ansys.utilities.local_instancemanager_server.plugins import importlib_metadata


def check_result_config(path, expected):
    with open(path) as f:
        _config = json.load(f)
    assert _config == expected


def make_mock_entrypoint(product_name, launcher_method, launcher_kls):
    mock_entrypoint = Mock(spec=importlib_metadata.EntryPoint)
    mock_entrypoint.name = f"{product_name}.{launcher_method}"
    mock_entrypoint.load = Mock(return_value=launcher_kls)
    return mock_entrypoint
