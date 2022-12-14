from functools import partial
from typing import Dict
from unittest.mock import Mock

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

import pytest

from ansys.tools.local_product_launcher import config, plugins
from ansys.tools.local_product_launcher.interface import LAUNCHER_CONFIG_T, LauncherProtocol


@pytest.fixture(autouse=True)
def reset_config():
    """Reset the configuration at the start of each test."""
    config.reset_config()


def get_mock_entrypoints_from_plugins(
    target_plugins: Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]
):
    res = []
    for product_name, launchers in target_plugins.items():
        for launch_mode, launcher_kls in launchers.items():
            mock_entrypoint = Mock(spec=importlib_metadata.EntryPoint)
            mock_entrypoint.name = f"{product_name}.{launch_mode}"
            mock_entrypoint.load = Mock(return_value=launcher_kls)
            res.append(mock_entrypoint)
    return res


@pytest.fixture
def monkeypatch_entrypoints_from_plugins(monkeypatch):
    def inner(target_plugins):
        monkeypatch.setattr(
            plugins,
            "_get_entry_points",
            partial(get_mock_entrypoints_from_plugins, target_plugins=target_plugins),
        )

    return inner
