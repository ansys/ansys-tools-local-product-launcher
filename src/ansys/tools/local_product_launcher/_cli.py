import dataclasses
import json
import textwrap
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, cast

import click

from ._plugins import get_all_plugins
from .config import (
    _get_config_path,
    get_launch_mode_for,
    is_configured,
    save_config,
    set_config_for,
)
from .interface import LAUNCHER_CONFIG_T, METADATA_KEY_DOC, METADATA_KEY_NOPROMPT, LauncherProtocol


def format_prompt(*, field_name: str, description: Optional[str]) -> str:
    """Get the formatted prompt string from its field name and description."""
    prompt = f"\n{field_name}:"
    if description is not None:
        prompt += f"\n" + textwrap.indent(description, " " * 4)
    prompt += "\n"
    return prompt


_OVERWRITE_DEFAULT_FLAG_NAME = "overwrite_default"
_DEFAULT_STR = "default"


def get_subcommands_from_plugins(
    *, plugins: Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]
) -> Sequence[click.Command]:
    """Construct 'configure' subcommands from the plugins."""
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
            for field in dataclasses.fields(launcher_config_kls):
                option = get_option_from_field(field)
                launch_mode_command.params.append(option)

            extra_kwargs_overwrite_option = dict()
            if is_configured(product_name=product_name):
                current_launch_mode = get_launch_mode_for(product_name=product_name)
                if current_launch_mode != launch_mode:
                    extra_kwargs_overwrite_option = dict(
                        prompt=(
                            f"\nOverwrite default launch mode for {product_name} "
                            f"(currently set to '{current_launch_mode}')?"
                        ),
                        show_default=True,
                    )

            launch_mode_command.params.append(
                click.Option(
                    [f"--{_OVERWRITE_DEFAULT_FLAG_NAME}"],
                    is_flag=True,
                    **extra_kwargs_overwrite_option,  # type: ignore
                )
            )

            product_command.add_command(launch_mode_command)

    return all_product_commands


class JSONParamType(click.ParamType):
    """Implements interpreting options as JSON.

    An empty string is interpreted as None.
    """

    name = "json"

    def convert(self, value: Any, param: Any, ctx: Any) -> Any:
        """Implement string to dict conversion."""
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        if value == _DEFAULT_STR:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Cannot decode JSON value '{value}'") from e


def get_option_from_field(field: dataclasses.Field[Any]) -> click.Option:
    """Construct a click.Option from a dataclass field.

    Convert the field type, default, and metadata to the corresponding
    click.Option.
    """
    type_ = {
        int: int,
        str: str,
        bool: bool,
    }.get(field.type, JSONParamType())

    if field.default is not dataclasses.MISSING:
        default = field.default
        if default is None:
            default = _DEFAULT_STR
            if not isinstance(type_, JSONParamType):
                raise ValueError(f"Invalid default value 'None' for {type_} type.")
    elif field.default_factory is not dataclasses.MISSING:
        default = field.default_factory()
    else:
        default = None

    description = field.metadata.get(METADATA_KEY_DOC, None)
    prompt_required = not field.metadata.get(METADATA_KEY_NOPROMPT, False)
    return click.Option(
        [f"--{field.name}"],
        prompt=format_prompt(
            field_name=field.name,
            description=description,
        ),
        help=description,
        type=type_,
        default=default,
        prompt_required=prompt_required,
    )


def config_writer_callback_factory(
    launcher_config_kls: Type[LAUNCHER_CONFIG_T], product_name: str, launch_mode: str
) -> Callable[..., None]:
    """Construct the callback for updating the config file."""

    def _config_writer_callback(**kwargs: Dict[str, Any]) -> None:
        overwrite_default = cast(bool, kwargs.pop(_OVERWRITE_DEFAULT_FLAG_NAME, False))
        config = launcher_config_kls(**kwargs)
        set_config_for(
            product_name=product_name,
            launch_mode=launch_mode,
            config=config,
            overwrite_default=overwrite_default,
        )
        save_config()
        click.echo(f"\nUpdated {_get_config_path()}")

    return _config_writer_callback


def build_cli(plugins: Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]) -> click.Group:
    """Construct the CLI from the plugins."""
    _cli = click.Group()

    all_subcommands = get_subcommands_from_plugins(plugins=plugins)

    @_cli.group(invoke_without_command=True)
    @click.pass_context
    def configure(ctx: click.Context) -> None:
        """
        Configure the options for a specific product and launch mode.

        The available products and launch modes are determined dynamically
        from the installed plugins.

        To get a list of products:

        .. code:: bash

            ansys-launcher configure

        To get a list of launch mode for a given product:

        .. code:: bash

            ansys-launcher configure <PRODUCT_NAME>

        To configure a product launch mode:

        .. code:: bash

            ansys-launcher configure <PRODUCT_NAME> <LAUNCH_MODE>

        """
        if ctx.invoked_subcommand is None:
            if not plugins:
                click.echo("No plugins configured")

    for subcommand in all_subcommands:
        configure.add_command(subcommand)
    return _cli


# Needs to be defined at the module level, since this is what the [tool.poetry.scripts]
# entry point refers to.
cli = build_cli(plugins=get_all_plugins())

if __name__ == "__main__":
    cli()
