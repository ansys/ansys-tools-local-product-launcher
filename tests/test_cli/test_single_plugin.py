from click.testing import CliRunner
import pydantic
import pytest

from ansys.utilities.local_instancemanager_server import cli, interface
from tests.test_cli.common import check_result_config

from .common import make_mock_entrypoint


class MockConfig(pydantic.BaseModel):
    int_field: int
    str_field: str


class MockLauncher(interface.LauncherProtocol[MockConfig]):
    CONFIG_MODEL = MockConfig


TEST_PRODUCT = "my_product"
TEST_LAUNCHER_METHOD = "my_launcher"

EXPECTED_CONFIG = {
    TEST_PRODUCT: {
        "configs": {TEST_LAUNCHER_METHOD: {"int_field": 1, "str_field": "value"}},
        "launch_mode": TEST_LAUNCHER_METHOD,
    }
}


@pytest.fixture
def mock_entrypoints():
    mock_entrypoint = make_mock_entrypoint(TEST_PRODUCT, TEST_LAUNCHER_METHOD, MockLauncher)
    return (mock_entrypoint,)


def test_cli_no_plugins():
    command = cli.build_cli_from_entrypoints(tuple())
    runner = CliRunner()
    result = runner.invoke(command, ["configure"])
    assert result.exit_code == 0
    assert "No plugins" in result.output


def test_cli_mock_plugin(mock_entrypoints):
    command = cli.build_cli_from_entrypoints(mock_entrypoints)
    assert "configure" in command.commands
    configure_group = command.commands["configure"]

    assert len(configure_group.commands) == 1
    assert TEST_PRODUCT in configure_group.commands

    product_group = configure_group.commands[TEST_PRODUCT]
    assert TEST_LAUNCHER_METHOD in product_group.commands

    launcher_command = product_group.commands[TEST_LAUNCHER_METHOD]
    assert len(launcher_command.params) == 2
    assert [p.name for p in launcher_command.params] == ["int_field", "str_field"]


@pytest.mark.parametrize(
    ["commands", "prompts"],
    [
        (
            ["configure", TEST_PRODUCT, TEST_LAUNCHER_METHOD, "--int_field=1", "--str_field=value"],
            [],
        ),
        (["configure", "my_product", "my_launcher", "--str_field=value"], ["1"]),
        (["configure", "my_product", "my_launcher", "--int_field=1"], ["value"]),
        (["configure", "my_product", "my_launcher"], ["1", "value"]),
    ],
)
def test_run_cli(temp_config_file, mock_entrypoints, commands, prompts):
    cli_command = cli.build_cli_from_entrypoints(mock_entrypoints)
    runner = CliRunner()
    result = runner.invoke(
        cli_command,
        commands,
        input="\n".join(prompts) if prompts else None,
    )

    assert result.exit_code == 0
    check_result_config(temp_config_file, EXPECTED_CONFIG)


def test_run_cli_throws_on_incorrect_type(temp_config_file, mock_entrypoints):
    cli_command = cli.build_cli_from_entrypoints(mock_entrypoints)
    runner = CliRunner()
    result = runner.invoke(
        cli_command,
        ["configure", TEST_PRODUCT, TEST_LAUNCHER_METHOD, "--int_field=TEXT", "--str_field=value"],
    )
    assert result.exit_code == 1
