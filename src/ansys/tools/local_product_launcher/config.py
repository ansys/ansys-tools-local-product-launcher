import json
import os
import pathlib
from typing import Any, Dict, Optional, Type, cast

import appdirs
import pydantic
import pydantic.generics

from ._plugins import get_config_model
from .interface import LAUNCHER_CONFIG_T

__all__ = ["get_config_for", "set_config_for", "is_configured", "get_launch_mode_for"]


_CONFIG_PATH_ENV_VAR_NAME = "ANSYS_LAUNCHER_CONFIG_PATH"


class _ProductConfig(pydantic.BaseModel):
    launch_mode: str
    configs: Dict[str, Any]


class _LauncherConfiguration(pydantic.BaseModel):
    __root__: Dict[str, _ProductConfig]


_CONFIG: Optional[_LauncherConfiguration] = None


def get_launch_mode_for(*, product_name: str, launch_mode: Optional[str] = None) -> str:
    if launch_mode is not None:
        return launch_mode
    return _get_config()[product_name].launch_mode


def get_config_for(*, product_name: str, launch_mode: Optional[str]) -> LAUNCHER_CONFIG_T:
    launch_mode = get_launch_mode_for(product_name=product_name, launch_mode=launch_mode)
    config_class: Type[LAUNCHER_CONFIG_T] = get_config_model(
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
    return cast(LAUNCHER_CONFIG_T, _get_config()[product_name].configs[launch_mode])


def is_configured(*, product_name: str, launch_mode: Optional[str] = None) -> bool:
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
    if is_configured(product_name=product_name):
        product_config = _get_config()[product_name]
        product_config.configs[launch_mode] = config
        if overwrite_default:
            product_config.launch_mode = launch_mode
    else:
        _get_config()[product_name] = _ProductConfig(
            launch_mode=launch_mode, configs={launch_mode: config}
        )


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


def _save_config() -> None:
    if _CONFIG is not None:
        file_path = _get_config_path()
        with open(file_path, "w") as out_f:
            out_f.write(_CONFIG.json())
