"""Tests for the 'plugins' module."""

import pydantic
import pytest

from ansys.tools.local_product_launcher import _plugins, interface

TEST_PRODUCT_A = "PRODUCT_A"
TEST_PRODUCT_B = "PRODUCT_B"
TEST_LAUNCH_MODE_A1 = "LAUNCHER_A1"
TEST_LAUNCH_MODE_A2 = "LAUNCHER_A2"
TEST_LAUNCH_MODE_B1 = "LAUNCHER_B1"


class MockConfigA1(pydantic.BaseModel):
    pass


class MockLauncherA1(interface.LauncherProtocol[MockConfigA1]):
    CONFIG_MODEL = MockConfigA1


class MockConfigA2(pydantic.BaseModel):
    pass


class MockLauncherA2(interface.LauncherProtocol[MockConfigA2]):
    CONFIG_MODEL = MockConfigA2


class MockConfigB1(pydantic.BaseModel):
    pass


class MockLauncherB1(interface.LauncherProtocol[MockConfigB1]):
    CONFIG_MODEL = MockConfigB1


PLUGINS = {
    TEST_PRODUCT_A: {
        TEST_LAUNCH_MODE_A1: MockLauncherA1,
        TEST_LAUNCH_MODE_A2: MockLauncherA2,
    },
    TEST_PRODUCT_B: {TEST_LAUNCH_MODE_B1: MockLauncherB1},
}


@pytest.fixture
def monkeypatch_entrypoints(monkeypatch_entrypoints_from_plugins):
    monkeypatch_entrypoints_from_plugins(PLUGINS)


def test_get_all_plugins(monkeypatch_entrypoints):
    assert _plugins.get_all_plugins() == PLUGINS


@pytest.mark.parametrize(
    "product_name,launch_mode,expected_config_model",
    [
        (TEST_PRODUCT_A, TEST_LAUNCH_MODE_A1, MockConfigA1),
        (TEST_PRODUCT_A, TEST_LAUNCH_MODE_A2, MockConfigA2),
        (TEST_PRODUCT_B, TEST_LAUNCH_MODE_B1, MockConfigB1),
    ],
)
def test_get_config_model(
    monkeypatch_entrypoints, product_name, launch_mode, expected_config_model
):
    assert (
        _plugins.get_config_model(product_name=product_name, launch_mode=launch_mode)
        == expected_config_model
    )


@pytest.mark.parametrize(
    "product_name,launch_mode,expected_launcher",
    [
        (TEST_PRODUCT_A, TEST_LAUNCH_MODE_A1, MockLauncherA1),
        (TEST_PRODUCT_A, TEST_LAUNCH_MODE_A2, MockLauncherA2),
        (TEST_PRODUCT_B, TEST_LAUNCH_MODE_B1, MockLauncherB1),
    ],
)
def test_get_launcher(monkeypatch_entrypoints, product_name, launch_mode, expected_launcher):
    assert (
        _plugins.get_launcher(product_name=product_name, launch_mode=launch_mode)
        == expected_launcher
    )


def test_get_launcher_inexistent():
    with pytest.raises(KeyError) as exc:
        _plugins.get_launcher(product_name="does_not_exist", launch_mode="does_not_exist")
    assert "No plugin found" in str(exc.value)
