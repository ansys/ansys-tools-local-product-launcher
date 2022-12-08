from typing import Any, Dict, Union

import click
import pydantic

from .config import CONFIG_HANDLER, CONFIGS_KEY, LAUNCH_MODE_KEY
from .plugins import get_entry_points


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
_DEFAULT_PRODUCT_CONFIG = {CONFIGS_KEY: {}}


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
            product_config = CONFIG_HANDLER.configuration.setdefault(
                product_name, _DEFAULT_PRODUCT_CONFIG
            )
            product_config[CONFIGS_KEY][launcher_name] = model.dict()
            # For now, set default launcher to latest modified
            product_config[LAUNCH_MODE_KEY] = launcher_name
            CONFIG_HANDLER.write_config_to_file()
            click.echo(f"Updated {CONFIG_HANDLER.config_path}")

        for field_name, field_details in launcher_config_kls.schema()["properties"].items():
            # TODO arg type
            description = field_details.get("description", None)
            click.option(
                f"--{field_name}",
                prompt=f"{field_name}{f' ({description})' if description else ''}",
                help=field_details.get("description", None),
            )(_launcher_configure_command)
        product_command.command(name=launcher_name)(_launcher_configure_command)


build_cli_from_entrypoints()

if __name__ == "__main__":
    cli()
