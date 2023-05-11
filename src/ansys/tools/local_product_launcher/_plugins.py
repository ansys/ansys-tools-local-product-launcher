import importlib.metadata
from typing import Dict, Tuple, Type

from .interface import LAUNCHER_CONFIG_T, LauncherProtocol

LAUNCHER_ENTRY_POINT = "ansys.tools.local_product_launcher.launcher"


def get_launcher(
    *, product_name: str, launch_mode: str
) -> Type[LauncherProtocol[LAUNCHER_CONFIG_T]]:
    """Get the launcher plugin for a given product and launch mode."""
    ep_name = f"{product_name}.{launch_mode}"
    for entrypoint in _get_entry_points():
        if entrypoint.name == ep_name:
            return entrypoint.load()  # type: ignore
    else:
        raise KeyError(f"No plugin found for '{ep_name}'.")


def get_config_model(*, product_name: str, launch_mode: str) -> Type[LAUNCHER_CONFIG_T]:
    """Get the configuration model for a given product and launch mode."""
    return get_launcher(product_name=product_name, launch_mode=launch_mode).CONFIG_MODEL


def get_all_plugins() -> Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]]:
    """Get mapping {"<product_name>": {"<launch_mode>": Launcher}} containing all plugins."""
    res: Dict[str, Dict[str, LauncherProtocol[LAUNCHER_CONFIG_T]]] = dict()
    for entry_point in _get_entry_points():
        product_name, launch_mode = entry_point.name.split(".")
        res.setdefault(product_name, dict())
        res[product_name][launch_mode] = entry_point.load()
    return res


def _get_entry_points() -> Tuple[importlib.metadata.EntryPoint, ...]:
    """Get all Local Product Launcher plugin entry points."""
    try:
        return importlib.metadata.entry_points()[LAUNCHER_ENTRY_POINT]  # type: ignore
    except KeyError:
        return tuple()
