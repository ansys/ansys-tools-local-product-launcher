from typing import Any, Callable, Dict, List, Tuple, Type, Union

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

import click

from .config import CONFIG_HANDLER, CONFIGS_KEY, LAUNCH_MODE_KEY
from .interface import LAUNCHER_CONFIG_T
from .plugins import get_entry_points

_DEFAULT_PRODUCT_CONFIG: Dict[str, Union[str, Dict[str, Any]]]
_DEFAULT_PRODUCT_CONFIG = {CONFIGS_KEY: {}}


def get_subcommands_from_entrypoints(
    entry_points: Tuple[importlib_metadata.EntryPoint, ...],
) -> List[click.Command]:
    product_commands: Dict[str, Any] = {}
    for entry_point in entry_points:
        product_name, launcher_method = entry_point.name.split(".")
        product_command = product_commands.get(product_name, None)
        if product_command is None:
            product_command = product_commands.setdefault(product_name, click.Group(product_name))

        launcher_kls = entry_point.load()
        launcher_config_kls = launcher_kls.CONFIG_MODEL

        _config_writer_callback = config_writer_callback_factory(
            launcher_config_kls, product_name, launcher_method
        )
        launch_method_command = click.Command(launcher_method, callback=_config_writer_callback)
        for field_name, field_details in launcher_config_kls.schema()["properties"].items():
            # TODO arg type
            description = field_details.get("description", None)
            prompt = field_name if description is None else f"{field_name} ({description})"
            option = click.Option(f"--{field_name}", prompt=prompt, help=description)
            launch_method_command.params.append(option)

        product_command.add_command(launch_method_command)

    return list(product_commands.values())


def config_writer_callback_factory(
    launcher_config_kls: Type[LAUNCHER_CONFIG_T], product_name: str, launcher_method: str
) -> Callable[..., None]:
    def _config_writer_callback(**kwargs: Dict[str, Any]) -> None:
        model = launcher_config_kls(**kwargs)
        product_config = CONFIG_HANDLER.configuration.setdefault(
            product_name, _DEFAULT_PRODUCT_CONFIG
        )
        product_config[CONFIGS_KEY][launcher_method] = model.dict()
        # For now, set default launcher to latest modified
        product_config[LAUNCH_MODE_KEY] = launcher_method
        CONFIG_HANDLER.write_config_to_file()
        click.echo(f"Updated {CONFIG_HANDLER.config_path}")

    return _config_writer_callback


cli = click.Group()
configure = click.Group("configure")
cli.add_command(configure)

for subcommand in get_subcommands_from_entrypoints(get_entry_points()):
    configure.add_command(subcommand)

if __name__ == "__main__":
    cli()
