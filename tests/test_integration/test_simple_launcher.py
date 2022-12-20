from dataclasses import dataclass

import pytest

from ansys.tools.local_product_launcher import config, launch_product

from .simple_test_launcher import SimpleLauncher, SimpleLauncherConfig

PRODUCT_NAME = "TestProduct"
LAUNCH_MODE = "direct"


@dataclass
class OtherConfig:
    int_attr: int


@pytest.fixture(autouse=True)
def monkeypatch_entrypoints(monkeypatch_entrypoints_from_plugins):
    monkeypatch_entrypoints_from_plugins({PRODUCT_NAME: {"direct": SimpleLauncher}})


def test_default_config():
    config.set_config_for(
        product_name=PRODUCT_NAME, launch_mode=LAUNCH_MODE, config=SimpleLauncherConfig()
    )
    server = launch_product(PRODUCT_NAME)
    server.wait(timeout=10)
    server.stop()
    assert not server.check()


def test_explicit_config():
    server = launch_product(PRODUCT_NAME, launch_mode=LAUNCH_MODE, config=SimpleLauncherConfig())
    server.wait(timeout=10)
    server.stop()
    assert not server.check()


def test_invalid_launch_mode_raises():
    with pytest.raises(KeyError):
        launch_product(
            PRODUCT_NAME, launch_mode="invalid_launch_mode", config=SimpleLauncherConfig()
        )


def test_invalid_config_raises():
    with pytest.raises(TypeError):
        launch_product(PRODUCT_NAME, launch_mode=LAUNCH_MODE, config=OtherConfig(int_attr=3))


def test_contextmanager():
    with launch_product(
        PRODUCT_NAME, launch_mode=LAUNCH_MODE, config=SimpleLauncherConfig()
    ) as server:
        server.wait(timeout=10)
        assert server.check()
    assert not server.check()
