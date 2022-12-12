import pytest

from ansys.utilities.local_instancemanager_server import config


@pytest.fixture
def temp_config_file(monkeypatch, tmp_path):
    output_path = tmp_path / "config.json"

    def get_config_path_patched():
        return output_path

    monkeypatch.setattr(config, "get_config_path", get_config_path_patched)
    yield output_path


@pytest.fixture(autouse=True)
def reset_config():
    config.reset_config()
