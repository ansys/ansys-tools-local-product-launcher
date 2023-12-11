from ansys.tools.local_product_launcher._plugins import (
    get_all_plugins,
    get_config_model,
    get_launcher,
)


def test_plugin_found():
    plugin_dict = get_all_plugins()
    assert "pkg_with_entrypoint" in plugin_dict
    assert "test_entry_point" in plugin_dict["pkg_with_entrypoint"]


def test_get_launcher():
    launcher = get_launcher(product_name="pkg_with_entrypoint", launch_mode="test_entry_point")
    assert launcher.__name__ == "Launcher"


def test_get_config_model():
    config_model = get_config_model(
        product_name="pkg_with_entrypoint", launch_mode="test_entry_point"
    )
    assert config_model.__name__ == "LauncherConfig"
