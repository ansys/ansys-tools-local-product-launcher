import json
import pathlib

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol
from .plugins import get_entry_points

import click
import pydantic


@click.group()
@click.pass_context
def cli(ctx):
    config_handler = ConfigHandler()
    ctx.ensure_object(dict)
    ctx.obj["handler"] = config_handler


@cli.group()
@click.pass_context
def configure(ctx):
    pass


def product_command_factory(name: str):
    @configure.group(name=name)
    @click.pass_context
    def _wrapped(ctx):
        pass

    return _wrapped


def build_cli_from_entrypoints():
    product_commands = {}
    for entry_point in get_entry_points():
        product_name, launcher_name = entry_point.name.split(".")
        product_command = product_commands.get(product_name, None)
        if product_command is None:
            product_command = product_commands.setdefault(product_name, product_command_factory(product_name))

        launcher_kls = entry_point.load()  # type: LauncherProtocol
        launcher_config_kls = launcher_kls.CONFIG_MODEL  # type: LAUNCHER_CONFIG_T

        @click.pass_context
        def _launcher_configure_command(ctx, **kwargs):
            config_handler = ctx.obj["handler"]
            model = launcher_config_kls(**kwargs)  # type: pydantic.BaseModel
            config_handler.configuration.setdefault(product_name, {})[launcher_name] = model.dict()
            config_handler.write_config_to_file()

        for field_name, field_details in launcher_config_kls.schema()["properties"].items():
            click.option(f"--{field_name}", prompt=True)(_launcher_configure_command)
        product_command.command(name=launcher_name)(_launcher_configure_command)


class ConfigHandler:
    _default_path = "config.json"

    def __init__(self):
        if pathlib.Path(self._default_path).exists():
            self._read_config_from_file()
        else:
            self.configuration = {}

    def _read_config_from_file(self):
        with open(self._default_path, "r") as f:
            self.configuration = json.load(f)

    def write_config_to_file(self):
        with open(self._default_path, "w") as f:
            json.dump(self.configuration, f)


build_cli_from_entrypoints()

if __name__ == '__main__':
    cli()
