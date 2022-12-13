from typing import Any, Callable, Dict, List, Sequence, Type

import click

from .config import ProductConfig, get_config, get_config_path, save_config
from .interface import LAUNCHER_CONFIG_T, LauncherProtocol
from .plugins import get_all_plugins


def get_subcommands_from_plugins(
    *, plugins: Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]
) -> Sequence[click.Command]:

    all_product_commands: List[click.Group] = []
    for product_name, launch_mode_configs in plugins.items():
        product_command = click.Group(product_name)
        all_product_commands.append(product_command)
        for launch_mode, launcher_kls in launch_mode_configs.items():
            launcher_config_kls = launcher_kls.CONFIG_MODEL

            _config_writer_callback = config_writer_callback_factory(
                launcher_config_kls, product_name, launch_mode
            )
            launch_mode_command = click.Command(launch_mode, callback=_config_writer_callback)
            for field_name, field_details in launcher_config_kls.schema()["properties"].items():
                # TODO arg type
                description = field_details.get("description", None)
                prompt = field_name if description is None else f"{field_name} ({description})"
                option = click.Option([f"--{field_name}"], prompt=prompt, help=description)
                launch_mode_command.params.append(option)

            product_command.add_command(launch_mode_command)

    return all_product_commands


def config_writer_callback_factory(
    launcher_config_kls: Type[LAUNCHER_CONFIG_T], product_name: str, launch_mode: str
) -> Callable[..., None]:
    def _config_writer_callback(**kwargs: Dict[str, Any]) -> None:
        config = get_config()
        model = launcher_config_kls(**kwargs)

        if product_name not in config:
            config[product_name] = ProductConfig(
                configs={launch_mode: model}, launch_mode=launch_mode
            )
        else:
            config[product_name].configs.update({launch_mode: model})
            # For now, set default launcher to latest modified
            config[product_name].launch_mode = launch_mode
        save_config()
        click.echo(f"Updated {get_config_path()}")

    return _config_writer_callback


def build_cli(plugins: Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]) -> click.Group:
    _cli = click.Group()

    all_subcommands = get_subcommands_from_plugins(plugins=plugins)

    @_cli.group(invoke_without_command=True)
    @click.pass_context
    def configure(ctx: click.Context) -> None:
        if ctx.invoked_subcommand is None:
            if not plugins:
                click.echo("No plugins configured")
            # ctx.invoked_subcommand = "ACP"
        # else:
        # ctx.invoke(all_subcommands[0].commands["direct"])
        # raise (ValueError(type(ctx.invoked_subcommand), ctx.invoked_subcommand))
        # pass

    for subcommand in all_subcommands:
        configure.add_command(subcommand)
    return _cli


# Needs to be defined at the module level, since this is what the [tool.poetry.scripts]
# entry point refers to.
cli = build_cli(plugins=get_all_plugins())

if __name__ == "__main__":
    cli()
