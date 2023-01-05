import pytest

from ansys.tools.local_product_launcher import config

pytest.register_assert_rewrite("test_cli.common")


@pytest.fixture
def temp_config_file(monkeypatch, tmp_path):
    output_path = tmp_path / "config.json"

    def get_config_path_patched():
        return output_path

    monkeypatch.setattr(config, "_get_config_path", get_config_path_patched)
    yield output_path
