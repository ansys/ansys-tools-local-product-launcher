"""Tools for managing the Product Launcher configuration.

Manage the default configuration for launching products. The configuration
is loaded from / stored to a ``config.json`` file.
By default, this file is located in the user config directory (platform-dependent).
Its location can be specified explicitly with the ``ANSYS_LAUNCHER_CONFIG_PATH``
environment variable.
"""

import dataclasses
import json
import os
import pathlib
from typing import Any, Dict, Optional, Type, cast

import appdirs

from ._plugins import get_config_model
from .interface import LAUNCHER_CONFIG_T, DataclassProtocol

__all__ = [
    "get_config_for",
    "set_config_for",
    "is_configured",
    "get_launch_mode_for",
    "save_config",
]


_CONFIG_PATH_ENV_VAR_NAME = "ANSYS_LAUNCHER_CONFIG_PATH"


@dataclasses.dataclass
class _ProductConfig:
    launch_mode: str
    configs: Dict[str, Any]


@dataclasses.dataclass
class _LauncherConfiguration:
    __root__: Dict[str, _ProductConfig]


_CONFIG: Optional[_LauncherConfiguration] = None


def get_launch_mode_for(*, product_name: str, launch_mode: Optional[str] = None) -> str:
    """Get the default launch mode configured for a product.

    Parameters
    ----------
    product_name :
        The product whose launch mode  is retrieved.
    launch_mode :
        If not ``None``, this value is returned.

    Returns
    -------
    :
        The launch mode for the product.
    """
    if launch_mode is not None:
        return launch_mode
    try:
        return _get_config()[product_name].launch_mode
    except KeyError as exc:
        raise KeyError(f"No configuration defined for product name '{product_name}'") from exc


def get_config_for(*, product_name: str, launch_mode: Optional[str]) -> DataclassProtocol:
    """Get the configuration object for a (product, launch_mode) combination.

    Retrieve the default configuration object for the product. If the
    ``launch_mode`` is given, the configuration for that mode is returned.
    Otherwise, the default launch mode configuration is returned.

    Parameters
    ----------
    product_name :
        The product whose configuration is returned.
    launch_mode :
        The launch mode whose configuration is returned.

    Returns
    -------
    :
        The configuration object.

    Raises
    ------
    KeyError
        If the requested configuration does not exist.
    TypeError
        If the configuration type does not match the type specified by
        the launcher plugin.
    """
    launch_mode = get_launch_mode_for(product_name=product_name, launch_mode=launch_mode)
    config_class: Type[DataclassProtocol] = get_config_model(
        product_name=product_name, launch_mode=launch_mode
    )
    config_entry = _get_config()[product_name].configs[launch_mode]
    if isinstance(config_entry, dict):
        _get_config()[product_name].configs[launch_mode] = config_class(**config_entry)
    else:
        if not isinstance(config_entry, config_class):
            raise TypeError(
                f"Configuration is of wrong type '{type(config_entry)}', should be '{config_class}'"
            )
    return cast(DataclassProtocol, _get_config()[product_name].configs[launch_mode])


def is_configured(*, product_name: str, launch_mode: Optional[str] = None) -> bool:
    """Check if a configuration exists for the product / launch mode.

    Parameters
    ----------
    product_name :
        The product whose configuration is checked.
    launch_mode :
        The launch mode whose configuration is checked. If ``None``, the
        default launch mode is used.
    """
    try:
        get_config_for(product_name=product_name, launch_mode=launch_mode)
        return True
    except KeyError:
        return False


def set_config_for(
    *,
    product_name: str,
    launch_mode: str,
    config: LAUNCHER_CONFIG_T,
    overwrite_default: bool = False,
) -> None:
    """Set the configuration for a given product and launch mode.

    Update the configuration by setting the configuration for the
    given product and launch mode.
    Note that this method only updates the in-memory configuration, and
    does not store it to file.

    Parameters
    ----------
    product_name :
        Name of the product whose configuration is updated.
    launch_mode :
        Launch mode to which the configuration applies.
    config :
        The configuration object.
    overwrite_default :
        If ``True``, the default launch mode for the product is
        changed to ``launch_mode``.
    """
    if is_configured(product_name=product_name):
        product_config = _get_config()[product_name]
        product_config.configs[launch_mode] = config
        if overwrite_default:
            product_config.launch_mode = launch_mode
    else:
        _get_config()[product_name] = _ProductConfig(
            launch_mode=launch_mode, configs={launch_mode: config}
        )


def save_config() -> None:
    """Store the configuration to disk.

    Save the current in-memory configuration to the ``config.json`` file.
    """
    if _CONFIG is not None:
        file_path = _get_config_path()
        # Convert to JSON before saving; in this way, errors during
        # JSON encoding will not clobber the config file.
        config_json = json.dumps(dataclasses.asdict(_CONFIG)["__root__"], indent=2)
        with open(file_path, "w") as out_f:
            out_f.write(config_json)


def _get_config() -> Dict[str, _ProductConfig]:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = _load_config()
    return _CONFIG.__root__


def _load_config() -> _LauncherConfiguration:
    config_path = _get_config_path()
    if not config_path.exists():
        return _LauncherConfiguration(__root__={})
    with open(config_path, "r") as in_f:
        return _LauncherConfiguration(
            __root__={key: _ProductConfig(**val) for key, val in json.load(in_f).items()}
        )


def _reset_config() -> None:
    global _CONFIG
    _CONFIG = None


def _get_config_path() -> pathlib.Path:
    if _CONFIG_PATH_ENV_VAR_NAME in os.environ:
        config_path = pathlib.Path(os.environ[_CONFIG_PATH_ENV_VAR_NAME])
        if not config_path.parent.exists():
            raise FileNotFoundError(
                f"The directory {config_path.parent} specified in the "
                f"{_CONFIG_PATH_ENV_VAR_NAME} environment variable does not exist."
            )

    else:
        config_path_dir = pathlib.Path(
            appdirs.user_config_dir("ansys_tools_local_product_launcher")
        )
        config_path = config_path_dir / "config.json"
        try:
            # Set up data directory
            config_path_dir.mkdir(exist_ok=True, parents=True)
        except OSError as exc:
            raise type(exc)(
                f"Unable to create config directory '{config_path_dir}'.\n"
                f"Error:\n{exc}\n\n"
                "Override the default config file path by setting the environment "
                f"variable '{_CONFIG_PATH_ENV_VAR_NAME}'."
            ) from exc
    return config_path
