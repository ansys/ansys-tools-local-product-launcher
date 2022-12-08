import pytest

from ansys.utilities.local_instancemanager_server import config


@pytest.fixture
def temp_config_file(monkeypatch, tmp_path):
    output_path = tmp_path / "config.json"
    monkeypatch.setattr(config.ConfigurationHandler, "config_path", output_path)
    yield output_path
