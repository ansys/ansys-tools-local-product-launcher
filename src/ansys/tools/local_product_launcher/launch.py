from __future__ import annotations

from typing import Optional, Type

from .config import get_config_for, get_launch_mode_for
from .interface import LAUNCHER_CONFIG_T, LauncherProtocol
from .plugins import get_launcher
from .server_handle import ServerHandle


def launch_product(
    product_name: str,
    config: Optional[LAUNCHER_CONFIG_T] = None,
    launch_mode: Optional[str] = None,
) -> ServerHandle:
    # if launch_mode is None and config is not None:
    #     raise ValueError(
    #         "When explicitly passing a 'config', the 'launch_mode' "
    #         "also needs to be specified."
    #     )

    launch_mode = get_launch_mode_for(product_name=product_name, launch_mode=launch_mode)

    launcher_klass: Type[LauncherProtocol[LAUNCHER_CONFIG_T]] = get_launcher(
        product_name=product_name,
        launch_mode=launch_mode,
    )

    if config is None:
        config = get_config_for(product_name=product_name, launch_mode=launch_mode)
    if not isinstance(config, launcher_klass.CONFIG_MODEL):
        raise TypeError(
            f"Incompatible config of type '{type(config)} supplied, "
            f"needs '{launcher_klass.CONFIG_MODEL}'."
        )
    return ServerHandle(launcher=launcher_klass(config=config))
