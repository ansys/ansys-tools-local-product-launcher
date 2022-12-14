from __future__ import annotations

from typing import Optional, Type

from ._plugins import get_launcher
from .config import get_config_for, get_launch_mode_for
from .interface import LAUNCHER_CONFIG_T, LauncherProtocol
from .product_instance import ProductInstance


def launch_product(
    product_name: str,
    config: Optional[LAUNCHER_CONFIG_T] = None,
    launch_mode: Optional[str] = None,
) -> ProductInstance:
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
    return ProductInstance(launcher=launcher_klass(config=config))
