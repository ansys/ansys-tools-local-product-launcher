from __future__ import annotations

from typing import Optional, Type, cast

from .config import CONFIGS_KEY, LAUNCH_MODE_KEY, ConfigurationHandler
from .interface import LAUNCHER_CONFIG_T, LauncherProtocol, ServerType
from .plugins import get_launcher
from .server_handle import GrpcServerHandle, ServerHandle


def launch_product(
    product_name: str,
    config: Optional[LAUNCHER_CONFIG_T] = None,
    launch_mode: Optional[str] = None,
) -> ServerHandle:
    config_handler = ConfigurationHandler()
    if launch_mode is None:
        if config is not None:
            raise ValueError(
                "When explicitly passing a 'config', the 'launch_mode' "
                "also needs to be specified."
            )
        try:
            launch_mode_evaluated = cast(
                str, config_handler.configuration[product_name][LAUNCH_MODE_KEY]
            )
        except KeyError as exc:
            raise KeyError(
                f"No 'launch_mode' configuration found for product '{product_name}'."
            ) from exc
    else:
        launch_mode_evaluated = launch_mode

    launcher_klass: Type[LauncherProtocol[LAUNCHER_CONFIG_T]] = get_launcher(
        product_name=product_name,
        launch_mode=launch_mode_evaluated,
    )

    if config is None:
        try:
            product_config = config_handler.configuration[product_name][CONFIGS_KEY]
            config_json = product_config[launch_mode_evaluated]
        except KeyError as exc:
            raise KeyError(
                f"No configuration found for product '{product_name}', "
                f"launch_mode='{launch_mode_evaluated}'."
            ) from exc
        config = launcher_klass.CONFIG_MODEL(**config_json)
    else:
        if not isinstance(config, launcher_klass.CONFIG_MODEL):
            raise TypeError(
                f"Incompatible config of type '{type(config)} supplied, "
                f"needs '{launcher_klass.CONFIG_MODEL}'."
            )
    if launcher_klass.SERVER_TYPE is ServerType.GRPC:
        server_klass: Type[ServerHandle] = GrpcServerHandle
    else:
        server_klass = ServerHandle
    return server_klass(launcher=launcher_klass(config=config))
