from functools import lru_cache
import json
import os
import pathlib
from typing import Any, Dict

import appdirs

__all__ = ["CONFIG_HANDLER", "LAUNCH_MODE_KEY", "CONFIGS_KEY"]

_CONFIG_PATH_ENV_VAR_NAME = "LOCAL_PIM_CONFIG_PATH"

LAUNCH_MODE_KEY = "launch_mode"
CONFIGS_KEY = "configs"


class _ConfigurationHandler:
    def __init__(self) -> None:
        if self.config_path.exists():
            self._read_config_from_file()
        else:
            self.configuration: Dict[Any, Any] = {}

    def _read_config_from_file(self) -> None:
        with open(self.config_path, "r") as f:
            self.configuration = json.load(f)

    def write_config_to_file(self) -> None:
        with open(self.config_path, "w") as f:
            json.dump(self.configuration, f)

    @property
    def config_path(self) -> pathlib.Path:
        return self._get_config_path()

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_config_path() -> pathlib.Path:
        if _CONFIG_PATH_ENV_VAR_NAME in os.environ:
            config_path = pathlib.Path(os.environ[_CONFIG_PATH_ENV_VAR_NAME])
            if not config_path.parent.exists():
                raise FileNotFoundError(
                    f"The directory {config_path.parent} specified in the "
                    f"{_CONFIG_PATH_ENV_VAR_NAME} environment variable does not exist."
                )

        else:
            config_path = pathlib.Path(appdirs.user_data_dir("local_pim")) / "config.json"
            try:
                # Set up data directory
                config_path.parent.mkdir(exist_ok=True)
            except OSError as exc:
                raise type(exc)(
                    f"Unable to create config directory '{config_path.parent}'.\n"
                    f"Error:\n{exc}\n\n"
                    "Override the default config file path by setting the environment "
                    f"variable '{_CONFIG_PATH_ENV_VAR_NAME}'."
                ) from exc
        return config_path


CONFIG_HANDLER = _ConfigurationHandler()
