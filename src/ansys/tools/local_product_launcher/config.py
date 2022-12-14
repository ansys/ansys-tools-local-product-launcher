import json
import os
import pathlib
from typing import Dict, Optional, Type

import appdirs
import pydantic

from .interface import LAUNCHER_CONFIG_T
from .plugins import get_config_model

__all__ = ["ConfigurationHandler"]

_CONFIG_PATH_ENV_VAR_NAME = "ANSYS_LAUNCHER_CONFIG_PATH"


class ProductConfig(pydantic.BaseModel):
    launch_mode: str
    configs: Dict[str, pydantic.BaseModel]


class LauncherConfiguration(pydantic.BaseModel):
    __root__: Dict[str, ProductConfig]


CONFIG: Optional[LauncherConfiguration] = None


def get_config() -> Dict[str, ProductConfig]:
    global CONFIG
    if CONFIG is None:
        CONFIG = load_config()
    return CONFIG.__root__


def get_launch_mode_for(*, product_name: str, launch_mode: Optional[str] = None) -> str:
    if launch_mode is not None:
        return launch_mode
    return get_config()[product_name].launch_mode


def get_config_for(*, product_name: str, launch_mode: Optional[str]) -> LAUNCHER_CONFIG_T:
    launch_mode = get_launch_mode_for(product_name=product_name, launch_mode=launch_mode)
    config_class: Type[LAUNCHER_CONFIG_T] = get_config_model(
        product_name=product_name, launch_mode=launch_mode
    )
    return config_class(**get_config()[product_name].configs[launch_mode].dict())


def is_configured(*, product_name: str, launch_mode: Optional[str] = None) -> bool:
    try:
        get_config_for(product_name=product_name, launch_mode=launch_mode)
        return True
    except KeyError:
        return False


def set_config(
    *,
    product_name: str,
    launch_mode: str,
    config: LAUNCHER_CONFIG_T,
    overwrite_default: bool = False,
) -> None:
    try:
        product_config = get_config()[product_name]
        product_config.configs[launch_mode] = config
        if overwrite_default:
            product_config.launch_mode = launch_mode
    except KeyError:
        get_config()[product_name] = ProductConfig(
            launch_mode=launch_mode, configs={launch_mode: config}
        )


def load_config() -> LauncherConfiguration:
    config_path = get_config_path()
    if not config_path.exists():
        return LauncherConfiguration(__root__={})
    with open(config_path, "r") as in_f:
        return LauncherConfiguration(
            __root__={key: ProductConfig(**val) for key, val in json.load(in_f).items()}
        )


def reset_config() -> None:
    global CONFIG
    CONFIG = None


def get_config_path() -> pathlib.Path:
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


def save_config() -> None:
    if CONFIG is not None:
        file_path = get_config_path()
        with open(file_path, "w") as out_f:
            out_f.write(CONFIG.json())
