from __future__ import annotations

from typing import Optional, Type, cast

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol, ServerType
from .plugins import get_launcher
from .server_handle import GrpcServerHandle, ServerHandle

LAUNCH_METHOD_KEY = "launch_method"
CONFIGS_KEY = "configs"
CONFIG = {
    "ACP": {
        "launch_method": "direct",
        "configs": {
            "direct": {
                "binary_path": "C:\\Program Files\\ANSYS Inc\\v232\\ACP\\acp_grpcserver.exe",
                "stdout_file": "D:\\tmp\\out.txt",
                "stderr_file": "D:\\tmp\\err.txt",
            },
            "docker": {},
        },
    }
}


def launch_product(
    product_name: str,
    config: Optional[LAUNCHER_CONFIG_T] = None,
    launch_method: Optional[str] = None,
) -> ServerHandle:
    if launch_method is None:
        if config is not None:
            raise ValueError(
                "When explicitly passing a 'config', the 'launch_method' "
                "also needs to be specified."
            )
        try:
            launch_method_evaluated = cast(str, CONFIG[product_name][LAUNCH_METHOD_KEY])
        except KeyError as exc:
            raise KeyError(
                f"No 'launch_method' configuration found for product '{product_name}'."
            ) from exc
    else:
        launch_method_evaluated = launch_method

    launcher_klass: Type[LauncherProtocol[LAUNCHER_CONFIG_T]] = get_launcher(
        product_name=product_name,
        launch_method=launch_method_evaluated,
    )

    if config is None:
        try:
            config_json = CONFIG[product_name][CONFIGS_KEY][launch_method_evaluated]  # type: ignore
        except KeyError as exc:
            raise KeyError(
                f"No configuration found for product '{product_name}', "
                f"launch_method='{launch_method_evaluated}'."
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
