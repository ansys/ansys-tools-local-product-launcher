from click.testing import CliRunner
import pydantic

from ansys.tools.local_product_launcher import cli, interface

from .common import check_result_config

TEST_PRODUCT_A = "PRODUCT_A"
TEST_PRODUCT_B = "PRODUCT_B"
TEST_LAUNCH_MODE_A1 = "LAUNCHER_A1"
TEST_LAUNCH_MODE_A2 = "LAUNCHER_A2"
TEST_LAUNCH_MODE_B1 = "LAUNCHER_B1"


class MockConfigA1(pydantic.BaseModel):
    field_a1: int


class MockLauncherA1(interface.LauncherProtocol[MockConfigA1]):
    CONFIG_MODEL = MockConfigA1


class MockConfigA2(pydantic.BaseModel):
    field_a2: int


class MockLauncherA2(interface.LauncherProtocol[MockConfigA2]):
    CONFIG_MODEL = MockConfigA2


class MockConfigB1(pydantic.BaseModel):
    field_b1: int


class MockLauncherB1(interface.LauncherProtocol[MockConfigB1]):
    CONFIG_MODEL = MockConfigB1


PLUGINS = {
    TEST_PRODUCT_A: {
        TEST_LAUNCH_MODE_A1: MockLauncherA1,
        TEST_LAUNCH_MODE_A2: MockLauncherA2,
    },
    TEST_PRODUCT_B: {TEST_LAUNCH_MODE_B1: MockLauncherB1},
}


def test_cli_structure():
    command = cli.build_cli(PLUGINS)
    assert "configure" in command.commands
    configure_group = command.commands["configure"]

    assert TEST_PRODUCT_A in configure_group.commands
    assert TEST_PRODUCT_B in configure_group.commands

    assert TEST_LAUNCH_MODE_A1 in configure_group.commands[TEST_PRODUCT_A].commands
    assert TEST_LAUNCH_MODE_A2 in configure_group.commands[TEST_PRODUCT_A].commands
    assert TEST_LAUNCH_MODE_B1 in configure_group.commands[TEST_PRODUCT_B].commands

    assert (
        configure_group.commands[TEST_PRODUCT_A].commands[TEST_LAUNCH_MODE_A1].params[0].name
        == "field_a1"
    )


def test_configure_single_product_launcher(temp_config_file):
    cli_command = cli.build_cli(PLUGINS)
    runner = CliRunner()
    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT_A, TEST_LAUNCH_MODE_A1, "--field_a1=1"],
    )

    assert result.exit_code == 0
    expected_config = {
        TEST_PRODUCT_A: {
            "configs": {
                TEST_LAUNCH_MODE_A1: {"field_a1": 1},
            },
            "launch_mode": TEST_LAUNCH_MODE_A1,
        }
    }
    check_result_config(temp_config_file, expected_config)


def test_configure_two_product_launchers(temp_config_file):
    cli_command = cli.build_cli(PLUGINS)
    runner = CliRunner()
    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT_A, TEST_LAUNCH_MODE_A1, "--field_a1=1"],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT_A, TEST_LAUNCH_MODE_A2, "--field_a2=2"],
    )
    assert result.exit_code == 0

    expected_config = {
        TEST_PRODUCT_A: {
            "configs": {
                TEST_LAUNCH_MODE_A1: {"field_a1": 1},
                TEST_LAUNCH_MODE_A2: {"field_a2": 2},
            },
            "launch_mode": TEST_LAUNCH_MODE_A1,
        }
    }
    check_result_config(temp_config_file, expected_config)


def test_configure_two_product_launchers_overwrite(temp_config_file):
    cli_command = cli.build_cli(PLUGINS)
    runner = CliRunner()
    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT_A, TEST_LAUNCH_MODE_A1, "--field_a1=1"],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT_A, TEST_LAUNCH_MODE_A2, "--field_a2=2", "--overwrite_default"],
    )
    assert result.exit_code == 0

    expected_config = {
        TEST_PRODUCT_A: {
            "configs": {
                TEST_LAUNCH_MODE_A1: {"field_a1": 1},
                TEST_LAUNCH_MODE_A2: {"field_a2": 2},
            },
            "launch_mode": TEST_LAUNCH_MODE_A2,
        }
    }
    check_result_config(temp_config_file, expected_config)


def test_configure_two_products(temp_config_file):
    cli_command = cli.build_cli(PLUGINS)
    runner = CliRunner()
    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT_A, TEST_LAUNCH_MODE_A1, "--field_a1=1"],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT_B, TEST_LAUNCH_MODE_B1, "--field_b1=3"],
    )
    assert result.exit_code == 0

    expected_config = {
        TEST_PRODUCT_A: {
            "configs": {
                TEST_LAUNCH_MODE_A1: {"field_a1": 1},
            },
            "launch_mode": TEST_LAUNCH_MODE_A1,
        },
        TEST_PRODUCT_B: {
            "configs": {
                TEST_LAUNCH_MODE_B1: {"field_b1": 3},
            },
            "launch_mode": TEST_LAUNCH_MODE_B1,
        },
    }
    import json

    with open(temp_config_file) as f:
        _config = json.load(f)
    assert _config == expected_config
    # check_result_config(temp_config_file, expected_config)
