from typing import Any, Callable, Dict, List, Tuple, Type, Union

try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

import click

from .config import CONFIGS_KEY, LAUNCH_MODE_KEY, ConfigurationHandler
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
        launch_mode_command = click.Command(launcher_method, callback=_config_writer_callback)
        for field_name, field_details in launcher_config_kls.schema()["properties"].items():
            # TODO arg type
            description = field_details.get("description", None)
            prompt = field_name if description is None else f"{field_name} ({description})"
            option = click.Option([f"--{field_name}"], prompt=prompt, help=description)
            launch_mode_command.params.append(option)

        product_command.add_command(launch_mode_command)

    return list(product_commands.values())


def config_writer_callback_factory(
    launcher_config_kls: Type[LAUNCHER_CONFIG_T], product_name: str, launcher_method: str
) -> Callable[..., None]:
    def _config_writer_callback(**kwargs: Dict[str, Any]) -> None:
        config_handler = ConfigurationHandler()
        model = launcher_config_kls(**kwargs)
        if product_name not in config_handler.configuration:
            config_handler.configuration[product_name] = {CONFIGS_KEY: {}}
        product_config = config_handler.configuration[product_name]
        product_config[CONFIGS_KEY][launcher_method] = model.dict()
        # For now, set default launcher to latest modified
        product_config[LAUNCH_MODE_KEY] = launcher_method
        config_handler.write_config_to_file()
        click.echo(f"Updated {config_handler.config_path}")

    return _config_writer_callback


def build_cli_from_entrypoints(entry_points) -> click.Group():
    _cli = click.Group()

    @_cli.group(invoke_without_command=True)
    @click.pass_context
    def configure(ctx) -> None:
        if ctx.invoked_subcommand is None:
            if not entry_points:
                click.echo("No plugins configured")

    for subcommand in get_subcommands_from_entrypoints(entry_points):
        configure.add_command(subcommand)
    return _cli


cli = build_cli_from_entrypoints(get_entry_points())

if __name__ == "__main__":
    cli()
