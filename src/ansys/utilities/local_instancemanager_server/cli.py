import json
import os
import pathlib
from typing import Any, Dict, Union
import warnings

import appdirs
import click
import pydantic

from .plugins import get_entry_points

USER_DATA_PATH: str
if "LOCAL_PIM_USERDATA_PATH" in os.environ:
    USER_DATA_PATH = os.environ["LOCAL_PIM_USERDATA_PATH"]
    if not os.path.isdir(USER_DATA_PATH):
        raise FileNotFoundError(f"Invalid LOCAL_PIM_USERDATA_PATH at {USER_DATA_PATH}")

else:
    USER_DATA_PATH = appdirs.user_data_dir("local_pim")
    try:
        # Set up data directory
        os.makedirs(USER_DATA_PATH, exist_ok=True)
    except Exception as e:
        warnings.warn(
            f'Unable to create `LOCAL_PIM_USERDATA_PATH` at "{USER_DATA_PATH}"\n'
            f"Error: {e}\n\n"
            "Override the default path by setting the environmental variable "
            "`LOCAL_PIM_USERDATA_PATH` to a writable path."
        )
        USER_DATA_PATH = ""


LOCAL_PIM_CONFIG_PATH: str = os.path.join(USER_DATA_PATH, "config.json")


@click.group()
def cli() -> None:
    pass


@cli.group()
def configure() -> None:
    pass


def product_command_factory(name: str) -> click.Group:
    @configure.group(name=name)
    def _wrapped() -> None:
        pass

    return _wrapped


_DEFAULT_PRODUCT_CONFIG: Dict[str, Union[str, Dict[str, Any]]]
_DEFAULT_PRODUCT_CONFIG = {"configs": {}}


def build_cli_from_entrypoints() -> None:
    product_commands: Dict[str, Any] = {}
    for entry_point in get_entry_points():
        product_name, launcher_name = entry_point.name.split(".")
        product_command = product_commands.get(product_name, None)
        if product_command is None:
            product_command = product_commands.setdefault(
                product_name, product_command_factory(product_name)
            )

        launcher_kls = entry_point.load()
        launcher_config_kls = launcher_kls.CONFIG_MODEL

        def _launcher_configure_command(**kwargs: Dict[str, Any]) -> None:
            model = launcher_config_kls(**kwargs)  # type: pydantic.BaseModel
            config_handler = ConfigurationHandler()
            product_config = config_handler.configuration.setdefault(
                product_name, _DEFAULT_PRODUCT_CONFIG
            )
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
    def __init__(self) -> None:
        if pathlib.Path(LOCAL_PIM_CONFIG_PATH).exists():
            self._read_config_from_file()
        else:
            self.configuration: Dict[Any, Any] = {}

    def _read_config_from_file(self) -> None:
        with open(LOCAL_PIM_CONFIG_PATH, "r") as f:
            self.configuration = json.load(f)

    def write_config_to_file(self) -> None:
        with open(LOCAL_PIM_CONFIG_PATH, "w") as f:
            json.dump(self.configuration, f)


build_cli_from_entrypoints()

if __name__ == "__main__":
    cli()
