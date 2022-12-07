import json
import os
import pathlib
import warnings

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol
from .plugins import get_entry_points

import appdirs
import click
import pydantic


if 'LOCAL_PIM_USERDATA_PATH' in os.environ:
    USER_DATA_PATH = os.environ['LOCAL_PIM_USERDATA_PATH']
    if not os.path.isdir(USER_DATA_PATH):
        raise FileNotFoundError(f'Invalid LOCAL_PIM_USERDATA_PATH at {USER_DATA_PATH}')

else:
    USER_DATA_PATH = appdirs.user_data_dir('local_pim')
    try:
        # Set up data directory
        os.makedirs(USER_DATA_PATH, exist_ok=True)
    except Exception as e:
        warnings.warn(
            f'Unable to create `LOCAL_PIM_USERDATA_PATH` at "{USER_DATA_PATH}"\n'
            f'Error: {e}\n\n'
            'Override the default path by setting the environmental variable '
            '`LOCAL_PIM_USERDATA_PATH` to a writable path.'
        )
        USER_DATA_PATH = ''

LOCAL_PIM_CONFIG_PATH = os.path.join(USER_DATA_PATH, "config.json")


@click.group()
def cli():
    pass


@cli.group()
def configure():
    pass


def product_command_factory(name: str):
    @configure.group(name=name)
    def _wrapped():
        pass

    return _wrapped

_DEFAULT_PRODUCT_CONFIG = {"configs": {}}


def build_cli_from_entrypoints():
    product_commands = {}
    for entry_point in get_entry_points():
        product_name, launcher_name = entry_point.name.split(".")
        product_command = product_commands.get(product_name, None)
        if product_command is None:
            product_command = product_commands.setdefault(product_name, product_command_factory(product_name))

        launcher_kls = entry_point.load()  # type: LauncherProtocol
        launcher_config_kls = launcher_kls.CONFIG_MODEL  # type: LAUNCHER_CONFIG_T

        def _launcher_configure_command(**kwargs):
            model = launcher_config_kls(**kwargs)  # type: pydantic.BaseModel
            config_handler = ConfigurationHandler()
            product_config = config_handler.configuration.setdefault(product_name, _DEFAULT_PRODUCT_CONFIG)
            product_config["configs"][launcher_name] = model.dict()
            # For now, set default launcher to latest modified
            product_config["launcher"] = launcher_name
            config_handler.write_config_to_file()
            click.echo(f"Updated {LOCAL_PIM_CONFIG_PATH}")

        for field_name, field_details in launcher_config_kls.schema()["properties"].items():
            # TODO arg type
            description = field_details.get("description", None)
            click.option(
                f"--{field_name}",
                prompt=f"{field_name}{f' ({description})' if description else ''}",
                help=field_details.get("description", None),
            )(_launcher_configure_command)
        product_command.command(name=launcher_name)(_launcher_configure_command)


class ConfigurationHandler:
    def __init__(self):
        if pathlib.Path(LOCAL_PIM_CONFIG_PATH).exists():
            self._read_config_from_file()
        else:
            self.configuration = {}

    def _read_config_from_file(self):
        with open(LOCAL_PIM_CONFIG_PATH, "r") as f:
            self.configuration = json.load(f)

    def write_config_to_file(self):
        with open(LOCAL_PIM_CONFIG_PATH, "w") as f:
            json.dump(self.configuration, f)


build_cli_from_entrypoints()

if __name__ == '__main__':
    cli()
